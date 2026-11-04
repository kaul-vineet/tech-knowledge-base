# Containers on the Mac mini: Colima (MIT)

Projects 03 and 08 need no containers. Project 05 can run the INDI server and simulators inside a Debian container
(`apt-get install indi-bin`) instead of building INDI natively; everything else runs as plain Python processes and
native tools (Ollama, Stellarium). Use this page only if a project's `mac_mini/README.md` asks for a container.

Colima ("containers on Lima") runs a small Linux VM with a container runtime on macOS; open source, MIT licence.
```zsh
brew install colima docker            # official alternatives: sudo port install colima | nix-env -iA nixpkgs.colima
colima start --cpu 4 --memory 8       # size it from mac_profile.py: leave the model server its budget
docker run --rm hello-world
colima stop                           # frees the VM's memory for Ollama and the simulations
```
- The default VM has 2 CPUs, 2 GiB memory and 100 GiB disk; change with `colima start --cpu N --memory GB` (stop first).
- The VM's memory comes out of the same unified memory as the models: `mac_profile.py`'s budget assumes no VM is
  running. Subtract the `--memory` you give Colima before choosing a model size.
- Ollama inside a container gets no Metal GPU on macOS (Ollama FAQ: no GPU passthrough in Docker Desktop on macOS):
  run Ollama natively, containers only for the services around it.
- Podman (Apache-2.0) is the cross-platform alternative used in `shared/WORKSTATION-SETUP.md` for the Windows PC.
Sources: https://github.com/abiosoft/colima (README: install, defaults, licence), Ollama FAQ.
