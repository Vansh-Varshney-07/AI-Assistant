# CLAI: actual REA static artifact investigation

Date: 27 October 2026. REA: locally built `rea-agents` 6.8.0 from the ignored clone; isolated Node 24.22.1. No CLAI installation or execution occurred.

## Artifact identity

- Official distribution: [CLAI v26.10.23 Windows setup](https://github.com/clairun/clai/releases/tag/v26.10.23).
- Installer: `clai_26.10.23_x64-setup.exe`, 12,175,851 bytes, SHA-256 `3105083921aa7405a101b9e1dea3fa77b07e3497ae173c6d88f07a3448618d68`, matching GitHub's published asset digest.
- 7-Zip 25.01 inspected the NSIS archive and extracted only `clai.exe`; it did not run the installer. The selected member is 49,461,248 bytes, SHA-256 `ea63b255bc7731db33b65c1aedb9c3c3299dea460e5524b5285038325c50c87f`.
- Acquisition records: `.local/rea-research/artifacts/clai/acquisition.json`. Extraction: `.local/rea-research/extracted/clai/clai.exe`.

## Actual REA commands and evidence

Each command used the private Node executable with `rea/scripts/rea.mjs`, appended `--format json`, and completed with CLI exit code 0. The GNU objdump follow-up retained a provider exit of 1 inside valid Evidence; it did not successfully inspect symbols. Complete original JSON, stderr and command/exit/elapsed-time records are under `.local/rea-research/results/clai/`.

| Command | Result | Evidence ID |
| --- | --- | --- |
| `inspect-desktop-application <extracted/clai>` | One native PE header examined; 340 selected bytes; complete within the one-file scan. No runtime family or component was established. | `ev_3e16dc1384224fbc3b8cbad35ddb3edf6374ae9b5db69cfaf59c32e423d5d5ab` |
| `inspect-pe-imports <clai.exe>` | Complete import-directory inspection: 32 DLL descriptors, 489 imports, no delay imports. | `ev_40229c315f92f718d7e34704b51e7ff469057556a89551d59a0c3f6e02887bdb` |
| `inspect-pe-certificates <clai.exe>` | PE security directory absent; no embedded WIN_CERTIFICATE entries inspected. This is not signature-chain validation or proof about catalog signatures. | `ev_d762d599fbb534422eae045866921903f2aacccbca67b529e042a3690a1060f8` |
| `inspect-pe-resources <clai.exe>` | Complete supported resource-tree inventory: 26 directory entries, 11 resources. Most payload interpretation remains opaque. | `ev_db422917cd2a9b690edddb3b54f37de4c6c21f4404ea18eb8064f8462770ac6e` |
| `inspect-rust-binary <clai.exe>` | No `.dep-v0` dependency metadata; a read-only `/rustc/` compiler-path marker was inferred. Functions/types and runtime behavior were not recovered. | `ev_39a385c9e715b4b2d7573ec6aefa8f803b4c20f53c355d2bba49d5f730b31ab7` |
| `inspect-with-objdump <clai.exe> symbols --command-timeout-ms 30000` | Existing `C:/MinGW/bin/objdump.exe` returned provider exit 1: `File format not recognized`. REA retained the failure, untruncated diagnostics and unchanged before/after artifact digest. | `ev_3569eaedf6423b5607cd3f7f098197490cd8d03db5a9361ee3abf256c7322e42` |

## Findings and their authority

**Observed in the shipped native artifact:** the PE imports include `CredReadW`, `BCryptGenRandom` and `CreateProcessW`. These establish declared import identities, not that a credential is stored safely, a process is sandboxed, or a given user action reaches these imports. No such security claim is made.

**Source-study evidence, separately labelled:** the previously inspected [InlineApprovalCard](https://github.com/clairun/clai/blob/a0b75e6f38288d3efdb0fc439a997a15dbfdda97/src/components/InlineApprovalCard.tsx) presents command segments, one-time decisions and the cross-workspace reach of persistent shared-agent permissions. The [Windows fallback runner](https://github.com/clairun/clai/blob/a0b75e6f38288d3efdb0fc439a997a15dbfdda97/src-tauri/src/assistant/sandbox/unsupported.rs) starts the command and delegates lifecycle handling; this does not establish Linux/macOS-style containment on Windows. These source findings are not attributed to REA and are not proven to match this release's embedded implementation byte for byte.

**Native follow-up:** after reading REA's GNU objdump integration guide, the existing GNU Binutils 2.28 executable was selected through `REA_OBJDUMP_COMMAND`; no tool was installed. The actual REA symbols operation failed at the provider's format recognition step, so symbol stripping is **unknown**, rather than established. No focused permission/UI symbol was identified and no whole-image or targeted disassembly was attempted. The ordinary standalone `objdump --version` observation is separate from the REA record, whose provider version remains null.

**Unresolved:** the embedded frontend, its native IPC targets and permission checks were not decompiled from this native executable. No deep decompiler was installed or invoked in this pass. The PE resource/import work and failed symbols operation do not answer that flow. UI layout, keyboard behavior, actual credential use and sandbox enforcement remain unobserved at runtime. This is a partial reverse-engineering result, not a completed security audit.

## Wayfinder-only adaptation

Use the reviewed workspace-aware attention and readable per-operation review layout as design references. Keep Wayfinder's existing exact immutable action proposal, main-owned confirmation, final-handler scope checks, expiry/revocation and receipt verification. Show actual workspace/task scope; do not copy permanent shared-agent allow rules, arbitrary shell execution or a Windows sandbox badge based on a permissions card.

No new Wayfinder capability, driver, runtime, agent or persistent memory system is proposed from these native findings. Shipped UI/permission-flow parity remains an explicit evidence gap rather than a basis for expanding authority.
