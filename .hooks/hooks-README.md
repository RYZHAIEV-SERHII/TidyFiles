If you place the ```commit-msg``` script directly in the ```.git/hooks/``` directory, you don’t need to configure it in
the ```.pre-commit-config.yaml``` file. <br/>
The ```.pre-commit-config.yaml``` file is used for managing hooks with the pre-commit framework, which is a separate
tool from Git’s native hooks.

However, if you want to use ```pre-commit``` to manage your hooks and still have _the commit-msg validation_, you should
place the script in a directory within your repository (not directly in ```.git/hooks/```) and reference it in the
```.pre-commit-config.yaml``` file.
Here’s how you can do it:

1. **Place the Script in a Directory**:<br/>
   Create a directory for your hooks (e.g., hooks) and place the ```commit-msg``` script there.

```bash
mkdir -p .hooks
chmod +x .hooks/commit-msg
```

2. **Configure .pre-commit-config.yaml**: <br/>
   Update your .pre-commit-config.yaml file to reference the script in the hooks directory:

```
repos:
  - repo: local
    hooks:
      - id: validate-commit-message
        name: Validate Commit Message
        entry: .hooks/commit-msg
        language: script
        stages: [commit-msg]
```

3. **Install the Pre-Commit Hook**: <br/>
   Run the following command to install the pre-commit hooks defined in your configuration file:

```bash
pre-commit install --hook-type commit-msg
```

This way, you can manage your commit message validation using the pre-commit framework while keeping your script
organized within your repository.
