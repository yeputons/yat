from repo_parse import parse_url, ParsedUrl

class TestParseGitHub:
    def test_root(self):
        assert parse_url("https://github.com/zuevmaxim/repo") == ParsedUrl("git@github.com:zuevmaxim/repo.git", "master", "")
        assert parse_url("https://github.com/zuevmaxim/repo.git") == ParsedUrl("git@github.com:zuevmaxim/repo.git", "master", "")

    def test_subdir(self):
        assert parse_url("https://github.com/zuevmaxim/repo/tree/yat") == ParsedUrl("git@github.com:zuevmaxim/repo.git", "yat", "")
        assert parse_url("https://github.com/tiginamaria/First/tree/master/HW5") == ParsedUrl("git@github.com:tiginamaria/First.git", "master", "HW5")
        assert parse_url("https://github.com/tiginamaria/First/tree/master/HW5/yat") == ParsedUrl("git@github.com:tiginamaria/First.git", "master", "HW5/yat")

    def test_file(self):
        assert parse_url("https://github.com/zuevmaxim/repo/blob/yat/folder.py") == ParsedUrl("git@github.com:zuevmaxim/repo.git", "yat", "folder.py")
        assert parse_url("https://github.com/tiginamaria/First/blob/master/HW5/folder.py") == ParsedUrl("git@github.com:tiginamaria/First.git", "master", "HW5/folder.py")

    def test_raw(self):
        assert parse_url("https://raw.githubusercontent.com/zuevmaxim/repo/yat/folder.py") == ParsedUrl("git@github.com:zuevmaxim/repo.git", "yat", "folder.py")
        assert parse_url("https://raw.githubusercontent.com/tiginamaria/First/master/HW5/folder.py") == ParsedUrl("git@github.com:tiginamaria/First.git", "master", "HW5/folder.py")


class TestParseGitLab:
    def test_root(self):
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "")
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW.git") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "")

    def test_subdir(self):
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/tree/master") ==  ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "")
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/tree/master/5") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "5")
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/tree/master/5/yat") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "5/yat")
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/tree/branch/5/yat") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "branch", "5/yat")

    def test_file(self):
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/blob/master/4/model.py") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "4/model.py")
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/blob/branch/4/model.py") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "branch", "4/model.py")

    def test_rase(self):
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/raw/master/4/model.py") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "master", "4/model.py")
        assert parse_url("https://gitlab.com/StairwayToHeaven/HW/raw/branch/4/model.py") == ParsedUrl("git@gitlab.com:StairwayToHeaven/HW.git", "branch", "4/model.py")