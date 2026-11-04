*** Comments ***
Lab 16 in Renode (pending-ci): build the firmware first (cargo build --release in ../firmware),
then run:  renode-test interrupt_race.robot
The fixed firmware must report lost=0 in every round. The racy firmware is only RECORDED:
whether the race shows up in emulation depends on Renode's instruction timing, so the
deterministic proof of the race is the host test (../test_fault.py, ../logic cargo test).

*** Variables ***
${UART}         sysbus.uart0
${ELF_DIR}      ${CURDIR}/../firmware/target/thumbv7em-none-eabihf/release
${PLATFORM}     ${CURDIR}/microbit-v2-sibling.repl

*** Keywords ***
Create Sibling
    [Arguments]    ${elf}
    Execute Command    mach create
    Execute Command    machine LoadPlatformDescription @${PLATFORM}
    Execute Command    sysbus LoadELF @${elf}
    Create Terminal Tester    ${UART}    defaultTimeout=60

*** Test Cases ***
Fixed Firmware Never Loses A Tick
    Create Sibling    ${ELF_DIR}/fixed
    Start Emulation
    Wait For Line On Uart    round=1 isr=
    Wait For Line On Uart    round=20 .* lost=0    treatAsRegex=true
    Wait For Line On Uart    done lost_total=0

Racy Firmware Runs And Reports
    Create Sibling    ${ELF_DIR}/microbit-v2-interrupt-race
    Start Emulation
    ${line}=    Wait For Line On Uart    done lost_total=
    Log To Console    racy firmware in Renode: ${line.line}
