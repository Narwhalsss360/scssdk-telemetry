# scssdk-telemetry

Telemetry channel/event/configuration metadata

This will build telemetry data from the scssdk.

---

*Notes:*

- The value for `CPP_INVALID_TYPE` is a type that is not declared anywhere, but if used for code-generation, it's best to probably just forward declare it.
- To modify, set `REWRITE_JSON = True`, make modifications to the data classes within the main function, before the write operation.