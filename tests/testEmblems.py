import json
import os
import unittest
from unittest import mock

import support
from support import (FakeNemoFile, commitFile, makeClonedRepository, makeDirectory,
                     makeFakeRepository, makeRepository, requiresGit,
                     resetSharedState, writeConfig, writeFile)

plugin = support.importPlugin("nemoRepoEmblems")

from nemoRepoCore import coreConfig, repoCache

gitEmblem = "emblem-repo-git"
markerEmblem = "emblem-repo-claude"
dirtyEmblem = "emblem-repo-dirty"
unpushedEmblem = "emblem-repo-unpushed"


class EmblemTestCase(unittest.TestCase):

    def setUp(self):
        resetSharedState()
        self.addCleanup(resetSharedState)
        self.provider = plugin.RepoEmblemProvider()

    def emblemsFor(self, path, **fileOptions):
        nemoFile = FakeNemoFile(path, **fileOptions)
        self.provider.update_file_info(nemoFile)
        return sorted(nemoFile.emblems)


class IndicatorSelectionTests(EmblemTestCase):

    def testDefaultsAreAllEnabled(self):
        self.assertEqual(sorted(plugin._enabledIndicators()),
                         ["claude_dir", "git_repo", "uncommitted_changes", "unpushed_commits"])

    def testDisabledEntryIsSkipped(self):
        writeConfig(coreConfig, {"indicators": {"git_repo": {"enabled": False}}})
        self.assertNotIn("git_repo", plugin._enabledIndicators())

    def testEntryWithoutEmblemIsSkipped(self):
        writeConfig(coreConfig, {"indicators": {"custom": {"enabled": True, "marker_file": "x"}}})
        self.assertNotIn("custom", plugin._enabledIndicators())

    def testNonObjectEntryIsSkipped(self):
        writeConfig(coreConfig, {"indicators": {"git_repo": True}})
        self.assertNotIn("git_repo", plugin._enabledIndicators())

    def testCustomEntryIsSelected(self):
        writeConfig(coreConfig, {"indicators": {
            "custom": {"enabled": True, "emblem": "emblem-ok", "marker_file": "x"}}})
        self.assertEqual(plugin._enabledIndicators()["custom"]["emblem"], "emblem-ok")


class MarkerMatchTests(unittest.TestCase):

    def testMarkerDirectory(self):
        path = makeDirectory()
        os.mkdir(os.path.join(path, ".venv"))
        self.assertTrue(plugin._markerMatches(path, {"marker_directory": ".venv"}))

    def testMarkerFile(self):
        path = makeDirectory()
        writeFile(path, "package.json", "{}")
        self.assertTrue(plugin._markerMatches(path, {"marker_file": "package.json"}))

    def testDirectoryDoesNotSatisfyMarkerFile(self):
        path = makeDirectory()
        os.mkdir(os.path.join(path, "package.json"))
        self.assertFalse(plugin._markerMatches(path, {"marker_file": "package.json"}))

    def testFileDoesNotSatisfyMarkerDirectory(self):
        path = makeDirectory()
        writeFile(path, ".venv")
        self.assertFalse(plugin._markerMatches(path, {"marker_directory": ".venv"}))

    def testEitherMarkerIsEnough(self):
        path = makeDirectory()
        writeFile(path, "setup.py")
        entry = {"marker_directory": ".venv", "marker_file": "setup.py"}
        self.assertTrue(plugin._markerMatches(path, entry))

    def testEntryWithoutMarkers(self):
        self.assertFalse(plugin._markerMatches(makeDirectory(), {}))


class MarkerEmblemTests(EmblemTestCase):

    def testPlainFolderGetsNothing(self):
        self.assertEqual(self.emblemsFor(makeDirectory()), [])

    def testDefaultMarkerDirectory(self):
        path = makeDirectory()
        os.mkdir(os.path.join(path, ".claude"))
        self.assertEqual(self.emblemsFor(path), [markerEmblem])

    def testMarkerRulesApplyInsideRepositories(self):
        repository = makeFakeRepository()
        nested = os.path.join(repository, "sub")
        os.makedirs(os.path.join(nested, ".claude"))
        self.assertEqual(self.emblemsFor(nested), [markerEmblem])

    def testCustomMarkerFileRule(self):
        writeConfig(coreConfig, {"indicators": {
            "node_project": {"enabled": True, "emblem": "emblem-important",
                             "marker_file": "package.json"}}})
        path = makeDirectory()
        writeFile(path, "package.json", "{}")
        self.assertEqual(self.emblemsFor(path), ["emblem-important"])

    def testGitIndicatorIgnoresMarkerFields(self):
        writeConfig(coreConfig, {"indicators": {"git_repo": {"marker_directory": "src"}}})
        path = makeDirectory()
        os.mkdir(os.path.join(path, "src"))
        self.assertEqual(self.emblemsFor(path), [])

    def testDisabledMarkerRule(self):
        writeConfig(coreConfig, {"indicators": {"claude_dir": {"enabled": False}}})
        path = makeDirectory()
        os.mkdir(os.path.join(path, ".claude"))
        self.assertEqual(self.emblemsFor(path), [])

    def testRegularFileIsSkipped(self):
        path = writeFile(makeDirectory(), "file.txt")
        self.assertEqual(self.emblemsFor(path, isDirectory=False), [])

    def testRemoteFolderIsSkipped(self):
        self.assertEqual(self.emblemsFor("/share", scheme="smb"), [])


@requiresGit
class GitEmblemTests(EmblemTestCase):

    def testRepositoryWithoutUpstream(self):
        self.assertEqual(self.emblemsFor(makeRepository()), sorted([gitEmblem, unpushedEmblem]))

    def testCleanClone(self):
        seed, clone = makeClonedRepository()
        self.assertEqual(self.emblemsFor(clone), [gitEmblem])

    def testDirtyClone(self):
        seed, clone = makeClonedRepository()
        writeFile(clone, "untracked.txt")
        self.assertEqual(self.emblemsFor(clone), sorted([gitEmblem, dirtyEmblem]))

    def testUnpushedCommit(self):
        seed, clone = makeClonedRepository()
        commitFile(clone, "local.txt", "local")
        self.assertEqual(self.emblemsFor(clone), sorted([gitEmblem, unpushedEmblem]))

    def testRepositoryWithMarker(self):
        seed, clone = makeClonedRepository()
        os.mkdir(os.path.join(clone, ".claude"))
        self.assertEqual(self.emblemsFor(clone), sorted([gitEmblem, markerEmblem]))

    def testFolderInsideRepositoryGetsNoGitEmblems(self):
        repository = makeRepository()
        nested = os.path.join(repository, "src")
        os.mkdir(nested)
        self.assertEqual(self.emblemsFor(nested), [])

    def testDisabledStateIndicatorsSkipGit(self):
        writeConfig(coreConfig, {"indicators": {
            "uncommitted_changes": {"enabled": False},
            "unpushed_commits": {"enabled": False}}})
        repository = makeRepository()
        with mock.patch.object(plugin.repoCache, "get") as get:
            self.assertEqual(self.emblemsFor(repository), [gitEmblem])
        get.assert_not_called()

    def testCustomEmblemName(self):
        writeConfig(coreConfig, {"indicators": {"git_repo": {"emblem": "emblem-default"}}})
        seed, clone = makeClonedRepository()
        self.assertEqual(self.emblemsFor(clone), ["emblem-default"])

    def testBrokenRepositoryGetsOnlyGitEmblem(self):
        path = makeDirectory()
        writeFile(path, ".git", "gitdir: /nonexistent\n")
        self.assertEqual(self.emblemsFor(path), [gitEmblem])

    def testFileObjectIsRegisteredForRedraw(self):
        repository = makeRepository()
        nemoFile = FakeNemoFile(repository)
        self.provider.update_file_info(nemoFile)
        repoCache.invalidate(repository)
        self.assertEqual(nemoFile.invalidations, 1)


class PackagingTests(unittest.TestCase):

    def testEveryDefaultEmblemShipsAnIcon(self):
        for key, entry in plugin.pluginDefaults["indicators"].items():
            with self.subTest(indicator=key):
                iconPath = os.path.join(support.repoRoot, "emblems", entry["emblem"] + ".svg")
                self.assertTrue(os.path.isfile(iconPath))

    def testExampleConfigMatchesDefaults(self):
        with open(os.path.join(support.repoRoot, "config.example.json")) as handle:
            example = json.load(handle)["indicators"]
        for key, entry in plugin.pluginDefaults["indicators"].items():
            with self.subTest(indicator=key):
                self.assertEqual(example[key]["emblem"], entry["emblem"])
                self.assertEqual(example[key]["enabled"], entry["enabled"])
                self.assertEqual(example[key].get("marker_directory"),
                                 entry.get("marker_directory"))

    def testExampleRulesAreDisabled(self):
        with open(os.path.join(support.repoRoot, "config.example.json")) as handle:
            example = json.load(handle)["indicators"]
        extras = set(example) - set(plugin.pluginDefaults["indicators"])
        self.assertEqual(extras, {"node_project", "virtualenv"})
        for key in extras:
            self.assertFalse(example[key]["enabled"])

    def testNameAndDescription(self):
        [entry] = plugin.RepoEmblemProvider().get_name_and_desc()
        self.assertTrue(entry.startswith("nemo-repo-emblems:::"))


if __name__ == "__main__":
    unittest.main()
