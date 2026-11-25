# Upload BakeryProduction v23 archive here

Upload the original file **Bakery_v23_FINAL_COMPLETE.zip** to this `incoming/` directory using GitHub's **Add file → Upload files**.

The GitHub Actions workflow `Import BakeryProduction v23 release` will automatically:

1. Check that the expected archive is present.
2. Extract the four ALP files, PNG resources, documentation and test scripts into `releases/v23/` **without altering relative paths**.
3. Run the static `verify_v23.py` consistency checks.
4. Commit the extracted files back into the repository.

**Do not rename the ZIP.**

If the workflow cannot push, check **Settings → Actions → General → Workflow permissions** and enable **Read and write permissions**, then rerun the workflow.

AnyLogic compilation and simulation must still be verified manually; the GitHub workflow performs XML structural checks only.
