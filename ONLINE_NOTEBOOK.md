# Run the notebook online

The repository includes a GitHub Codespaces configuration for both
`contents for hackertools.ipynb` and `Interactive-1.ipynb`. The Codespace runs
as `root` inside its isolated container. Root access applies only to the
container; it does not grant access to the Codespaces host.

## Start in GitHub Codespaces

1. Push this branch to a GitHub repository you control.
2. Open the repository on GitHub and select **Code → Codespaces → Create
   codespace on this branch**.
3. Wait for the container setup to finish.
4. Open either notebook:
   - `contents for hackertools.ipynb` for environment detection and explicit
     system-package installation.
   - `Interactive-1.ipynb` for the project-aware command helper and interactive
     CLI launcher.
5. Select the **Python 3** kernel and choose **Run All**.

The environment check should print:

```text
system           linux
is_root          True
...
Ready: root permissions are available inside the isolated container.
```

## Optional JupyterLab server

The browser-based Codespaces editor can run the notebook directly. If a
standalone JupyterLab UI is preferred, run this from the Codespaces terminal:

```bash
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

Codespaces forwards port 8888 privately by default. Keep it private and retain
Jupyter's generated access token.

## Permission boundary

The container intentionally does not use Docker `--privileged`, host filesystem
mounts, or a Docker socket mount. Those are not required for this notebook and
would weaken isolation. Use security tooling only on systems you own or have
explicit authorization to test.
