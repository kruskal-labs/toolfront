"""Unit tests for pattern matching algorithms - standalone functions."""

from sqlalchemy.engine.url import make_url

from toolfront.models.database import Database


# Create a concrete Database implementation for testing
class TestDatabase(Database):
    def __init__(self):
        super().__init__(url=make_url("sqlite:///:memory:"))

    async def test_connection(self):
        pass

    async def get_tables(self):
        pass

    async def inspect_table(self, table_path: str):
        pass

    async def sample_table(self, table_path: str, n: int = 5):
        pass

    async def query(self, code: str):
        pass


class TestRegexPatternMatching:
    """Test regex-based table pattern matching."""

    def setup_method(self):
        self.db = TestDatabase()

    def test_exact_match(self, sample_table_names):
        result = self.db._scan_tables_regex(sample_table_names, "users", 10)
        assert "users" in result
        assert len(result) <= 10

    def test_partial_match(self, sample_table_names):
        result = self.db._scan_tables_regex(sample_table_names, "user", 10)
        expected = ["users", "user_profiles"]
        assert all(name in result for name in expected)

    def test_case_insensitive_match(self, sample_table_names):
        result = self.db._scan_tables_regex(sample_table_names, "USER", 10)
        expected = ["users", "user_profiles"]
        assert all(name in result for name in expected)

    def test_wildcard_pattern(self, sample_table_names):
        result = self.db._scan_tables_regex(sample_table_names, ".*_data", 10)
        expected = ["customer_data", "payroll_data"]
        assert all(name in result for name in expected)

    def test_no_matches(self, sample_table_names):
        result = self.db._scan_tables_regex(sample_table_names, "nonexistent", 10)
        assert result == []

    def test_limit_respected(self, sample_table_names):
        # Pattern that matches many tables
        result = self.db._scan_tables_regex(sample_table_names, ".*", 3)
        assert len(result) == 3

    def test_empty_table_list(self):
        result = self.db._scan_tables_regex([], "users", 10)
        assert result == []


class TestJaroWinklerPatternMatching:
    """Test Jaro-Winkler similarity-based table pattern matching."""

    def setup_method(self):
        self.db = TestDatabase()

    def test_exact_match_highest_score(self, sample_table_names):
        result = self.db._scan_tables_jaro_winkler(sample_table_names, "users", 10)
        # Exact match should be first (highest similarity)
        assert result[0] == "users"

    def test_similar_names_ranked(self, sample_table_names):
        result = self.db._scan_tables_jaro_winkler(sample_table_names, "user", 10)
        # "users" should rank higher than "user_profiles" for pattern "user"
        assert result.index("users") < result.index("user_profiles")

    def test_limit_respected(self, sample_table_names):
        result = self.db._scan_tables_jaro_winkler(sample_table_names, "data", 3)
        assert len(result) == 3

    def test_empty_table_list(self):
        result = self.db._scan_tables_jaro_winkler([], "users", 10)
        assert result == []


class TestTfIdfPatternMatching:
    """Test TF-IDF similarity-based table pattern matching."""

    def setup_method(self):
        self.db = TestDatabase()

    def test_exact_token_match(self, sample_table_names):
        result = self.db._scan_tables_tf_idf(sample_table_names, "users", 5)
        # "users" should rank highly for exact token match
        assert "users" in result[:2]

    def test_empty_query_returns_empty(self, sample_table_names):
        result = self.db._scan_tables_tf_idf(sample_table_names, "", 5)
        assert result == []

    def test_empty_query_whitespace_only(self, sample_table_names):
        # Whitespace gets tokenized as a single token, so it won't be empty
        result = self.db._scan_tables_tf_idf(sample_table_names, "   ", 5)
        assert len(result) == 5  # Should return results based on TF-IDF scoring

    def test_no_valid_tokens_in_tables(self):
        # Tables with only separators that produce no tokens
        tables = ["___", "...", "---"]
        result = self.db._scan_tables_tf_idf(tables, "users", 3)
        assert result == []

    def test_limit_respected(self, sample_table_names):
        result = self.db._scan_tables_tf_idf(sample_table_names, "data", 3)
        assert len(result) == 3

    def test_empty_table_list(self):
        result = self.db._scan_tables_tf_idf([], "users", 10)
        assert result == []

    def test_single_table_list(self):
        result = self.db._scan_tables_tf_idf(["users"], "user", 10)
        assert result == ["users"]
