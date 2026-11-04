/* nRF52833 (micro:bit V2): 512 KB flash, 128 KB RAM (nRF52833 PS, "Memory").
   The nRF52840 that Renode models has 1 MB / 256 KB at the same start addresses,
   so this layout fits inside it - one of the reasons it is a close sibling. */
MEMORY
{
  FLASH : ORIGIN = 0x00000000, LENGTH = 512K
  RAM   : ORIGIN = 0x20000000, LENGTH = 128K
}
