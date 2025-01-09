# Developer notes

## vrnetlab module and vscode pylance

We added `.env` file in the root of the repo to add `common` dir to the python path so that the pylance extension can find the module.

However, if this doesn't work for you, add the following to the `settings.json` file in vscode:

```json
{
    "python.analysis.extraPaths": ["common"]
}
```
