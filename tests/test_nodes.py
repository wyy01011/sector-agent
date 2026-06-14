import unittest
from unittest.mock import patch

import pandas as pd

from agent.nodes import retrieve_market_data


class RetrieveMarketDataTests(unittest.TestCase):
    @staticmethod
    def make_state(company_data):
        return {
            "company_data": company_data,
            "errors": [],
            "route_taken": [],
        }

    @patch("agent.nodes.yf.Ticker")
    def test_returns_two_latest_closes(self, ticker):
        ticker.return_value.history.return_value = pd.DataFrame(
            {"Close": [100.0, 101.5, 103.0]}
        )
        state = self.make_state({"ticker": "TEST"})

        result = retrieve_market_data(state)

        ticker.return_value.history.assert_called_once_with(
            period="5d", auto_adjust=False
        )
        self.assertEqual(
            result["market_data"],
            {"latest_close": 103.0, "previous_close": 101.5},
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["route_taken"], ["retrieve_market_data"])

    @patch("agent.nodes.yf.Ticker")
    def test_handles_insufficient_prices(self, ticker):
        ticker.return_value.history.return_value = pd.DataFrame({"Close": [100.0]})
        state = self.make_state({"ticker": "TEST"})

        result = retrieve_market_data(state)

        self.assertIsNone(result["market_data"])
        self.assertEqual(
            result["errors"], ["Not enough market data found for ticker: TEST"]
        )
        self.assertEqual(result["route_taken"], ["retrieve_market_data"])

    @patch("agent.nodes.yf.Ticker")
    def test_handles_provider_errors(self, ticker):
        ticker.return_value.history.side_effect = RuntimeError("provider unavailable")
        state = self.make_state({"ticker": "TEST"})

        result = retrieve_market_data(state)

        self.assertIsNone(result["market_data"])
        self.assertEqual(
            result["errors"],
            ["Failed to retrieve market data for TEST: provider unavailable"],
        )
        self.assertEqual(result["route_taken"], ["retrieve_market_data"])


if __name__ == "__main__":
    unittest.main()
