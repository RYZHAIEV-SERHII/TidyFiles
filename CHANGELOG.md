# CHANGELOG


## v0.9.0 (2025-04-13)

### Documentation

- Enhance documentation and path resolution in configuration and history management
  ([`88de71d`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/88de71d90dc59ed403bcda1e4fdf8807a570a242))

### Features

- Add options to clear history and log, and show last session details
  ([`a2b43ce`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/a2b43ce51aa02b1a5534c70f5022690312e5bde3))

- Add progress bar support for undo and file operations in CLI
  ([`3a7a702`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/3a7a702051ace239e5e1d939f8ab0e52e54b5b08))

- Cast progress to ProgressBarProtocol for type checking in undo and file operations
  ([`9da1b9f`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/9da1b9ff675f1f04444de233af475fbd1aa7c281))

- Enhance logging control and improve type annotations in CLI and history modules
  ([`7b95625`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/7b9562544233e786985d806d52000d856e2bf01b))

- Enhance operation summary with detailed progress bars and duration tracking
  ([`d2b105f`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/d2b105fa4f2035f5444af262b4b793691a43e629))

- Implement log suppression decorator and enhance session management in history
  ([`6b54113`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/6b5411371005dd1fa8e66620f4c98fc12f7d03f1))

- Implement signal handling for graceful session closure and enhance history recovery
  ([`e8bd10d`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/e8bd10dde97f156eb7e8fc56642a823250044af7))

- Improve undo command handling with optional parameters and enhanced session management
  ([`8df9eb1`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/8df9eb16cad648c0af82bccc9bf656cf6bace200))

- Refine command options and enhance undo operation handling
  ([`75e1bb0`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/75e1bb02ae28aa2fddb54695be3b58c7278402b0))

### Refactoring

- Streamline test cases and enhance error handling for history and undo operations
  ([`e7b763b`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/e7b763b0d474d57137de4600f2fba81838bd95c8))

### Testing

- Add mock progress bar fixture and enhance output cleaning in tests
  ([`f7e505b`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/f7e505be4c1d57958f91e6df19899ceb673e807d))

- Enhance signal handling and improve test coverage for CLI operations
  ([`c4d8a33`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/c4d8a330e11766d48a9e63c0653f9a568a145b49))


## v0.8.2 (2025-04-08)

### Bug Fixes

- Improve log file path determination based on settings
  ([`ef1ef4e`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/ef1ef4ec4144c6b0d69db6e605a646a0ac7f964b))

### Code Style

- Add help descriptions for history and undo commands in CLI
  ([`171feaf`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/171feaff115022c6c002380cbe0fb090f73c22e2))

### Documentation

- Update README to reflect new file types and improved directory structure
  ([`4ad2bcf`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/4ad2bcfc9e82453edc81be42cd3a25bb6f0cb31d))


## v0.8.1 (2025-04-07)

### Bug Fixes

- Add support for additional file types in configuration
  ([`9a0f5fb`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/9a0f5fbaec08e8a687528310f8d1c549c7f04a3a))


## v0.8.0 (2025-04-06)


## v0.8.0-rc.1 (2025-04-06)

### Documentation

- Update README to include extensive format support and nested sorting features
  ([`a4d6e7e`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/a4d6e7edd4106619d1d4f7dd1cde834dfc5bc995))


## v0.8.0-b.1 (2025-04-06)

### Bug Fixes

- Improve error handling and display for undo operation in CLI
  ([`0b195b4`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/0b195b4d7c2f33defaf3bef58f8f02d0c849107a))

### Testing

- Enhance undo command tests with additional scenarios and edge cases
  ([`89e46ac`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/89e46ac9b30d0accc27c1c4c42a19f87adfb7c13))


## v0.8.0-a.1 (2025-04-06)

### Features

- Enhance cleaning plan structure to support nested categories and additional file types
  ([`5513a5b`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/5513a5bdb49a831f7018394d2499f5cbf5ea6069))


## v0.7.0 (2025-04-04)


## v0.7.0-rc.2 (2025-04-04)

### Bug Fixes

- Validate operation type in history processing to prevent invalid operations
  ([`628841d`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/628841d911c4ba807b85eb93fa4f41b40b9d736c))

### Documentation

- Update architecture and README to include operation history and session management features
  ([`af7baa7`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/af7baa778dc49a642d8d1fa6947b95c97e2f8e21))

### Testing

- Enhance CLI history and undo command tests with additional scenarios
  ([`3113802`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/3113802820ba0e84f5cf6f1b1bba2c82c36c51c2))


## v0.7.0-rc.1 (2025-04-03)

### Chores

- Update version to 0.7.0-b.1 and enhance operation history management
  ([`5a98836`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/5a9883650a6a2aaaaecdad61141e3498301cd78c))


## v0.7.0-b.1 (2025-04-03)

### Features

- Enhance CLI history and undo commands with session management and detailed output
  ([`23c263c`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/23c263c8bf1a4995c556705518bb2f6d8bdd0dbd))

- Enhance session management in CLI with detailed session info and improved operation handling
  ([`4e09ee2`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/4e09ee2e15d1aee7a1d521a0572d6a90db202681))

### Testing

- Enhance CLI tests to suppress Rich formatting and improve help command consistency
  ([`da43b2b`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/da43b2bedcfeeb17d3bab241775145b93c466736))

- Update CLI tests to explicitly request help and improve runner settings
  ([`bca1770`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/bca177003ee6e830ed5647876809d99f419b0ac3))

- Update CLI tests to set TERM environment variable and clean output for help command
  ([`42a57b3`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/42a57b3a9f4f971a3fd7885d92733c250bc9a40e))


## v0.7.0-a.1 (2025-04-02)

### Bug Fixes

- Enhance CLI options with default visibility and improved help display
  ([`078c95c`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/078c95c62a114000ccf8f3a11f5d058dbca82856))

- **ci**: Remove prerelease_token from main branch configuration
  ([`2d53c64`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/2d53c64903f7122ee9511ab37bc06748422331f9))

### Documentation

- Add comprehensive project documentation (architecture overview, code of conduct, and development
  guidelines) and update existing.
  ([`1ea7474`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/1ea747473e3875431c2c47c75114fe4b7fef58dc))

- Enhance documentation with additional details and formatting improvements across multiple files
  ([`a0ee26d`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/a0ee26d995965547d2a260a2e2677138bd1c0ec2))

- Update contributing guidelines and branch selection process
  ([`1965879`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/19658799af79ccb37482ecb94cbcdc8c0ea13144))

- Update README.md with upcoming release plans
  ([`319f4c1`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/319f4c1742a450a29e14e7d2f0bebdecb8310965))

- Update release workflow documentation with version bumping rules and example workflows
  ([`358c53e`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/358c53e14f3dda5358bb7abc1c7ff5562cb0c8fc))

### Features

- Implement operation history tracking with CLI commands for file management
  ([`ecf17a2`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/ecf17a29568b68fbc5c8c7358b55c94ab3e4f9a0))

### Testing

- Add comprehensive tests for get_settings and load_settings functions to handle various edge cases
  ([`4094346`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/40943467be3db0e014f49fb3efa74cdcdf52d939))

- Add new tests for create_plans function to cover various exclude scenarios and enhance coverage
  ([`4bdc1e0`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/4bdc1e07967e1b872440117164c4fc115d8c7cb7))

- Enhance test coverage for CLI and configuration handling and operations
  ([`e6f8cfb`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/e6f8cfbc84cc2ca49016e57c110c4ac1c33177c0))

- Enhance test fixtures for better isolation and cleanup
  ([`d117ad0`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/d117ad0a612a9c9c995fc56a9ce26268e047276b))

- Update CLI tests for output consistency and add operation history tests
  ([`460527f`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/460527f0965271464cea607f2ed04d68503f30b3))


## v0.6.12 (2025-03-26)

### Bug Fixes

- **ci**: Update release configuration to disable prerelease for main branch and add support for
  alpha, beta, and rc branches
  ([`5106d9d`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/5106d9d0a858bc0371646ad2348666ed614dba3e))


## v0.6.11 (2025-03-26)

### Bug Fixes

- **ci**: Enhance release workflow and prerelease tag handling. (rc)
  ([`bc7464e`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/bc7464ef2177fe5b066c4a447d244793d0c4e3e4))

- **ci**: Update build command in pyproject.toml to include pip installation. (rc)
  ([`847c45a`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/847c45a7ed7ebdc979678538305ab23fba3488e2))

- **rc**: Enhance commit message validation to support prerelease tags
  ([`adf8a65`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/adf8a65f60e6557608c7658737693cd7950a087d))

### Continuous Integration

- Enhance release workflow with improved job structure and safety checks
  ([`b84b0af`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/b84b0af450687d2aea3be87eca33e440d8116d93))

- Enhance release workflow with tag and branch verification checks
  ([`981b1e7`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/981b1e7e2a7af52f915aaacae4a6aa98040a803e))


## v0.6.10 (2025-03-25)

### Bug Fixes

- Update README to reflect new roadmap and upcoming features
  ([`d40d3ce`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/d40d3cea8835dd7b9acf62150263cc56419bd466))


## v0.6.9 (2025-03-24)

### Bug Fixes

- Enhance release workflow with version management and README updates
  ([`ab01983`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/ab01983ffa03df8bb5996226d870cb17a5e2f6e4))


## v0.6.8 (2025-03-24)

### Bug Fixes

- Update release workflow to generate and update README with latest release changes
  ([`a0bc045`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/a0bc045f35caeadd2706fd8be50960cbaace92c8))


## v0.6.7 (2025-03-24)

### Bug Fixes

- Add 'released' output to release workflow for better tracking
  ([`807d525`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/807d52543d04e94161e68ce6cdac4e0d18f37b77))


## v0.6.6 (2025-03-24)

### Bug Fixes

- Update release workflow to include version tag output and adjust permissions
  ([`888dbdb`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/888dbdb3c5e605ed15c0f302932d9487e6c56b7b))


## v0.6.5 (2025-03-24)

### Bug Fixes

- Update release workflow to pull latest changes and rebase before pushing README updates
  ([`ec55b86`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/ec55b866b75d8634642eb1a7080301541506bd35))


## v0.6.4 (2025-03-23)

### Chores

- Add Codecov configuration and update test coverage workflow
  ([`2a37854`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/2a37854fd9a29bec7b50829a5818b13934f2e991))

- Add GitHub Actions workflow for running tests with coverage
  ([`0b30c47`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/0b30c47f5650cd3bd49ffbe7e9e7da371ecb7381))

- Add step to create virtual environment in GitHub Actions workflow
  ([`2a59b74`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/2a59b74cd805b43c6d0f8a1bcce3610e75ae2e88))

- Enhance CLI with version display and improve settings validation
  ([`4e24c33`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/4e24c33739be30094930e997527eb2a54920f8c3))

- Enhance release workflow with semantic versioning and tag handling
  ([`62366be`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/62366be0e50db261aa7b695d2c43644777bf6fe9))

- Update GitHub Actions workflow for test coverage and Codecov integration
  ([`2fccc2b`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/2fccc2b6bb1ac4f50752cbfd7258d70ab7690d78))

### Performance Improvements

- Optimize project dependencies to enhance UX. update project structure and enhance development
  setup documentation
  ([`f4899ff`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/f4899ff98defab67f74ddffe4bb7004364211d30))

### Testing

- Add comprehensive test suite for TidyFiles application
  ([`b0f188a`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/b0f188a39e78a4d3719dbe83ee10ae2bab713980))


## v0.6.3 (2025-03-22)

### Bug Fixes

- Cli options parsing logic corrected, and now settings handled in proper way.
  ([`70af30f`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/70af30f21aa12ea06b276ce89bb3fffae12f02be))

- Logging error while trying to delete already deleted folders.
  ([`1649bd0`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/1649bd0fd951a8a1a6b1b950b4e0a860cdcf9871))

- Updated README.md
  ([`1f1aa12`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/1f1aa123dba5864d986546af8c942a73f2bd54dc))

### Chores

- Add CHANGELOG.md for version 0.6.3 with features, bug fixes, and documentation updates
  ([`1e2ef19`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/1e2ef1930994d2b12853c0d09bf5b79213921e86))

- Add GitHub Actions workflow for automated release process
  ([`e20511d`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/e20511d050233a5ed5c27a05fddea20d79ef9c6c))

- Bump version to 0.6.3
  ([`450b6e5`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/450b6e5efaa9b0506869187f070f43a8ff707b9c))

Version calculation from commit history: - Initial v0.1.0 - feat: logger config -> v0.2.0 - feat:
  main functionality -> v0.3.0 - fix: operations -> v0.3.1 - feat: config.py -> v0.4.0 - feat: CLI
  interface -> v0.5.0 - feat: main entrypoint -> v0.6.0 - fix: logging error -> v0.6.1 - fix: CLI
  options -> v0.6.2 - fix: README.md -> v0.6.3

Total changes: - MINOR (feat): 5 bumps - PATCH (fix): 4 bumps - Other (docs,chore,style): no version
  impact

- Implement commit message validation and update hooks documentation
  ([`9022a7a`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/9022a7a199f4876f82094214a0d0b2be20a06fdf))

- Update project metadata and add versioning information
  ([`18d8ac6`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/18d8ac626bc6f7bdc1c4c4f14a079625322fb6a7))

- Updated GitHub Actions workflow for automated release process
  ([`8d313b8`](https://github.com/RYZHAIEV-SERHII/TidyFiles/commit/8d313b8778a791f1e05f8280acd908b77d0170d8))
