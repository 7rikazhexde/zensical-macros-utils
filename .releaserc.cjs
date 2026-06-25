// semantic-release config (CommonJS so the release-notes template can be read
// from an external .hbs file at load time).
//
// Why a custom releaseNotes.template:
//   semantic-release-gitmoji's bundled default template only renders 5 gitmoji
//   groups (:boom: / :sparkles: / :bug: / :ambulance: / :lock:). Maintenance
//   releases are often driven by other gitmoji (:wrench:, :recycle:,
//   :arrow_up:, ...), for which the default template produces EMPTY release
//   notes. The template in .github/release-notes-template.hbs adds a section
//   for every gitmoji listed in releaseRules below, so patch/maintenance
//   releases get meaningful notes.
//
// PyPI publishing is intentionally NOT done here: the package is published
// from a developer machine with scripts/publish_to_pypi.py so the PyPI token
// (UV_PUBLISH_TOKEN) never has to live in CI. semantic-release only handles
// the version bump, changelog, commit, tag and GitHub Release.

const fs = require("fs");
const path = require("path");

const releaseNotesTemplate = fs.readFileSync(
  path.join(__dirname, ".github", "release-notes-template.hbs"),
  "utf8",
);

module.exports = {
  branches: ["main"],
  tagFormat: "v${version}",
  plugins: [
    [
      "semantic-release-gitmoji",
      {
        releaseRules: {
          major: [":boom:"],
          minor: [":sparkles:"],
          patch: [
            ":bug:",
            ":ambulance:",
            ":lock:",
            ":zap:",
            ":rocket:",
            ":wrench:",
            ":recycle:",
            ":fire:",
            ":arrow_up:",
            ":arrow_down:",
            ":pushpin:",
            ":pencil2:",
            ":globe_with_meridians:",
            ":alien:",
            ":card_file_box:",
          ],
        },
        releaseNotes: {
          template: releaseNotesTemplate,
        },
      },
    ],
    [
      "@semantic-release/exec",
      {
        // Bump pyproject.toml (uv), keep package.json (jest devDeps) in step,
        // then refresh the lockfile so uv.lock records the new version.
        prepareCmd:
          "uv version --no-sync ${nextRelease.version} && npm version ${nextRelease.version} --no-git-tag-version --no-commit-hooks --allow-same-version && uv lock",
      },
    ],
    [
      "@semantic-release/changelog",
      {
        changelogFile: "CHANGELOG.md",
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: [
          "pyproject.toml",
          "package.json",
          "package-lock.json",
          "uv.lock",
          "CHANGELOG.md",
        ],
        message:
          ":bookmark: chore(release): v${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
    "@semantic-release/github",
  ],
};
