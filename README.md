# DLSS-G Turing compatibility

Experimental Windows/C++ compatibility component for RTX 20 DLSS-G and
multi-frame generation, extracted from Theo's Render Pipeline (TRP).
The TRP candidate has an RTX 2060 volunteer run with runtime-reported x2/x3/x4/x6
output and loading recovery. This extraction has not been integrated into other
games. It is a developer component, not a standalone injector or end-user mod.

The instruction converter comes from **MFGAmpereUnlock-RenoDx** by ImDreamt,
mavismmg and nefh. Temporal/provider helpers derive from **RTX40MFG-Unlock** by
Michael Robles. TRP contributes the host integration, guarded PTX network
selection, failure diagnosis and tests. See [credits](THIRD-PARTY.md).

## Scope

- Physical RTX 20 detection; GTX 16 and unrelated SM75 devices are not admitted.
- SM75 PTX preparation, temporal program conversion and exact provider checks.
- Selection of the matching PTX endpoint networks instead of raw SM86 cubins.
- Scoped module/resolver interception, transactional writes and a synchronous
  stop at the first real GPU-module failure.
- Driver/OS rejection, SR isolation and repeated-creation regression fixtures.

The supported provider is **DLSS-G 310.9.1**, SHA-256
`FF6E90EB78B827927DFF5B4ECC6B1C870C2E9BCA29ED9F48C7D348CC9E170B82`.
Do not assume another DLL version has the same layout. The source also retains
the existing Ampere implementation to exercise isolation; this is not a general
adapter-support override. No NVIDIA DLLs, model weights or exported kernel
payloads are distributed here.

NR ran on the volunteer's RTX 2060 using TRP's existing runtime integration.
**This repository does not implement or unlock NR.** It does not include a game
renderer, swapchain presenter, menu or frame-pacing replacement.

## Build and test

Requires Windows x64, Visual Studio 2022 with C++/Windows SDK, CMake 3.21+, and
a locally supplied NVIDIA NGX SDK containing `include/nvsdk_ngx.h`.
Use the matching SDK headers from the TRP dependency setup; vendor files are
not downloaded by this build.

```powershell
cmake -S . -B out/build -G "Visual Studio 17 2022" -A x64 -DTRP_NGX_SDK_DIR="C:/path/to/ngx-sdk"
cmake --build out/build --config Release --parallel 2
ctest --test-dir out/build -C Release --output-on-failure
```

The normal CTests use synthetic programs/vendor doubles and no GPU dispatch.
`TRPTuringProviderAudit` and the Python network-selection check are explicit
manual tools. GPU probes are built but are **not** registered as CTests; invoke
them only deliberately. See [test instructions](tests/turing/README.md).
Tests and internal namespaces retain their TRP names to preserve source identity.

## Host integration

Add this directory with CMake `add_subdirectory`, then link
`dlssg_turing::compat`. The public entry points are in
[`extern/MFGAmpere/runtime.hpp`](extern/MFGAmpere/runtime.hpp).

The host must provide the actual rendering D3D12 device, an absolute runtime
directory, a log callback and a fatal callback that terminates on unrecoverable
kernel failure. Preparation must occur before Streamline initialization, from
a controlled host boundary rather than DllMain. Observe the physical adapter
before selecting this compatibility path; native and Ada routes remain host
decisions. Match TRP's startup-scope sequencing around the feature initialization
calls and verify the prepared state before use.

There is one owner/adapter/provider per process. Retain modules and published
allocations until process exit. There is no supported detach, hot reload or
recovery after a partial runtime failure. Keep `allowSeparateModules=false`
unless the host implements the coordinated separate-runtime ownership protocol;
it is not a generic conflict bypass. Existing `PluginPaths` module-normalization
helpers are retained; its Skyrim-specific `Directory()` helper is unused here.
`SourceDLSSGMFG.h` is retained for route-policy fixture coverage; the Skyrim
host implementation is not linked into this library.

The reference integration is [TRP](https://github.com/theosw/theosrenderpipeline),
at the commit recorded in [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json). Adaptation
to another host still needs its own lifetime, hook-order and rendering tests.

## Evidence and maintenance

The [extraction validation record](docs/VALIDATION.md) covers the standalone
build, 40 CTests, source identity and CPU-only real-provider checks.

See [RTX 2060 evidence and limits](docs/RTX20_COMPATIBILITY.md): about 25 minutes,
ENB/ReShade, DLSS Quality at 1080p output, x2/x3/x4/x6 and one loading recovery.
Temporary VRAM/presentation warnings and weapon jitter remain unresolved.
Other cards/games, image equivalence and measured display cadence are unverified.
The FP16 lowering changes accumulation order. No general quality or performance
improvement is claimed.

TRP remains the canonical source during this extraction stage. The manifest pins
every imported source/test/license file. Check the extraction with:

```powershell
python tools/check_source.py
python tools/check_source.py --trp C:/path/to/theosrenderpipeline
```

Make compatibility changes in TRP first, validate them there, then refresh this
snapshot and manifest from the reviewed commit. Do not maintain independent
fixes in both copies. The GPL licence and exceptions from TRP are retained for
this extraction; bundled third-party files retain their own notices and terms.
