# Adaptation Differences Across UE Versions

For soloAS 0.1.3.

This table records how soloAS on older UE versions differs from soloAS on the latest supported UE version, which is the reference.

## Core plugins

| Difference | Affected versions | Scope | Description | User impact |
| --- | --- | --- | --- | --- |
| Replication timing for mixed properties | 5.4, 5.5, 5.6 | Runtime | UE 5.4 through 5.6 continue checking the full property set for objects mixing ordinary and marked replication. UE 5.7 and later can check marked properties individually. **The UE-AS fork behaves the same in these versions.** | In UE 5.4 through 5.6, a property may still be sent without being marked as changed. For strict control that prevents such sends, use generic replication or upgrade to UE 5.7 or later. |
| Native resource cleanup callback | 5.4 | Runtime | UE 5.4 has no native early-cleanup callback, so payloads remain live during script destruction. **The UE-AS fork behaves the same in these versions.** | A throwing derived destructor can skip base payload cleanup. Avoid exceptions in destructors or release payloads explicitly during normal operation; use UE 5.5 or later when native cleanup before script destruction is required. |
| Externalized container override state | 5.4, 5.5, 5.6, 5.7 | Editor only | UE 5.4–5.7 lack externalized override state. On 5.4/5.5 soloAS explicitly rejects Externalized operations before import; on 5.6/5.7 the engine warns, ignores the operation and imports the value as an ordinary override. **The UE-AS fork behaves the same in these versions.** | Use a newer editor supporting externalization when the externalized semantics must be preserved. |
| Null object keys in incremental map overrides | 5.5 | Editor only | When override text import meets a null object map key, UE 5.5 rejects the key up front; the latest version hits a native assertion instead. **The UE-AS fork behaves the same in these versions.** | On 5.5 the key is not imported and the editor does not crash. Non-null keys are unaffected. |
| ListView scroll interpolation speed | 5.4 | Editor only | UE 5.4 lacks the newer scroll interpolation speed field and setter. **The UE-AS fork behaves the same in these versions.** | Native fixed-speed scrolling remains available, but its speed cannot be configured. |
| Python access to deleted script types | 5.4 | Editor only | UE 5.4 editor Python has no way to retire old types, so it may retain old type wrappers after a script class is deleted or renamed. **The UE-AS fork behaves the same in these versions.** | Restart the editor before accessing them through Python; game runtime is unaffected. |

## GAS

| Difference | Affected versions | Scope | Description | User impact |
| --- | --- | --- | --- | --- |
| Loose gameplay tag replication setting | 5.4, 5.5, 5.6 | Runtime | UE 5.4–5.6 do not provide a replication-count setting. soloAS exposes the same parameter as UE 5.8 on these versions, with None available and TagOnly aligned for server-authoritative calls. CountToOwner, TagAndCountToAll and SimulatedTagOnly raise explicit script errors. Count replication requires UE 5.7 or newer; SimulatedTagOnly requires UE 5.8 or newer. **The UE-AS fork behaves the same in these versions.** | None and TagOnly are available on legacy versions; count replication requires an engine upgrade. Parent tag counts during client prediction may differ from UE 5.8. |

## Enhanced Input

No user-visible differences have been confirmed; this does not mean behavior on every older version has been verified.

[API differences between the latest soloAS and the UE-AS fork](api-differences.md)
