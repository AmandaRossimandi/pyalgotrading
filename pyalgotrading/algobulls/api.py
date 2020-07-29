"""
Module for handling API calls to the [AlgoBulls](https://www.algobulls.com) backend.
"""

from json import JSONDecodeError

import requests

from .exceptions import AlgoBullsAPIBaseException, AlgoBullsAPIUnauthorizedError, AlgoBullsAPIInsufficientBalanceError, AlgoBullsAPIResourceNotFoundError, AlgoBullsAPIBadRequest, AlgoBullsAPIInternalServerErrorException, AlgoBullsAPIForbiddenError
from ..constants import TradingType, TradingReportType


class AlgoBullsAPI:
    """
    AlgoBulls API
    """
    # SERVER_ENDPOINT = 'https://api.algobulls.com/'
    SERVER_ENDPOINT = 'http://127.0.0.1:8000/'

    def __init__(self):
        """
        Init method that is used while creating an object of this class
        """
        self.headers = None
        self.__key_backtesting = None  # cstc id
        self.__key_papertrading = None  # cstc id
        self.__key_realtrading = None  # cstc id

    def set_access_token(self, access_token: str):
        """
        Sets access token to the header attribute, which is needed for APIs requiring authorization
        Package for interacting with AlgoBulls Algorithmic Trading Platform (https://www.algobulls.com)

        Args:
            access_token: Access token generated by logging to the URL given by the `get_authorization_url()` method
        """
        self.headers = {
            'Authorization': f'{access_token}'
        }

    def _send_request(self, method: str = 'get', endpoint: str = '', base_url: str = SERVER_ENDPOINT, params: [str, dict] = None, json_data: [str, dict] = None, requires_authorization: bool = True) -> dict:
        """
        Send the request to the platform
        Args:
            method: get
            endpoint: endpoint url
            base_url: base url
            params: parameters
            json_data: json data as body
            requires_authorization: True or False

        Returns:
            request status
        """
        url = f'{base_url}{endpoint}'
        headers = self.headers if requires_authorization else None
        response = requests.request(method=method, headers=headers, url=url, params=params, json=json_data)

        try:
            response_json = response.json()
        except JSONDecodeError:
            response_json = str(response)

        if response.status_code == 200:
            response_json = response.json()
            return response_json
        elif response.status_code == 400:
            raise AlgoBullsAPIBadRequest(method=method, url=url, response=response_json)
        elif response.status_code == 401:
            raise AlgoBullsAPIUnauthorizedError(method=method, url=url, response=response_json)
            # try:
            #     raise AlgoBullsAPIUnauthorizedError(method=method, url=url, response=response_json)
            # except AlgoBullsAPIUnauthorizedError as ex:
            #     print(f'{ex.get_error_type()}. {ex.response}')
        elif response.status_code == 402:
            raise AlgoBullsAPIInsufficientBalanceError(method=method, url=url, response=response_json)
        elif response.status_code == 403:
            raise AlgoBullsAPIForbiddenError(method=method, url=url, response=response_json)
        elif response.status_code == 404:
            raise AlgoBullsAPIResourceNotFoundError(method=method, url=url, response=response_json)
        elif response.status_code == 500:
            raise AlgoBullsAPIInternalServerErrorException(method=method, url=url, response=response_json)
        else:
            response.raw.decode_content = True
            raise AlgoBullsAPIBaseException(method=method, url=url, response=response_json)

    def __fetch_key(self, strategy_code, trading_type):
        # Add strategy to backtesting
        endpoint = f'v2/portfolio/strategy'
        json_data = {'strategyId': strategy_code, 'tradingType': trading_type.value}
        response = self._send_request(method='options', endpoint=endpoint, json_data=json_data)
        key = response.get('key')
        return key

    def __get_key(self, strategy_code, trading_type):
        if trading_type is TradingType.BACKTESTING:
            if self.__key_backtesting is None:
                self.__key_backtesting = self.__fetch_key(strategy_code=strategy_code, trading_type=TradingType.BACKTESTING)
            return self.__key_backtesting
        elif trading_type is TradingType.PAPERTRADING:
            if self.__key_papertrading is None:
                self.__key_papertrading = self.__fetch_key(strategy_code=strategy_code, trading_type=TradingType.PAPERTRADING)
            return self.__key_papertrading
        elif trading_type is TradingType.REALTRADING:
            if self.__key_realtrading is None:
                self.__key_realtrading = self.__fetch_key(strategy_code=strategy_code, trading_type=TradingType.REALTRADING)
            return self.__key_realtrading
        else:
            raise NotImplementedError

    def create_strategy(self, strategy_name: str, strategy_details: str, abc_version: str) -> dict:
        """
        Create a new strategy for the user on the AlgoBulls platform.

        Args:
            strategy_name: name of the strategy
            strategy_details: Python code of the strategy
            abc_version: value of one of the enums available under [AlgoBullsEngineVersion]()

        Returns:
            JSON Response received from AlgoBulls platform after (attempt to) creating a new strategy.

        Warning:
            For every user, the `strategy_name` should be unique. You cannot create multiple strategies with the same name.

        Info: ENDPOINT
            `POST` v2/user/strategy/build/python
        """
        json_data = {'strategyName': strategy_name, 'strategyDetails': strategy_details, 'abcVersion': abc_version}
        endpoint = f'v2/user/strategy/build/python'
        response = self._send_request(endpoint=endpoint, method='post', json_data=json_data)
        return response

    def update_strategy(self, strategy_name: str, strategy_details: str, abc_version: str) -> dict:
        """
        Update an already existing strategy on the AlgoBulls platform

        Args:
            strategy_name: name of the strategy
            strategy_details: Python code of the strategy
            abc_version: value of one of the enums available under `AlgoBullsEngineVersion`

        Returns:
            JSON Response received from AlgoBulls platform after (attempt to) updating an existing strategy.

        Info: ENDPOINT
            PUT v2/user/strategy/build/python
        """
        json_data = {'strategyName': strategy_name, 'strategyDetails': strategy_details, 'abcVersion': abc_version}
        endpoint = f'v2/user/strategy/build/python'
        response = self._send_request(endpoint=endpoint, method='put', json_data=json_data)
        return response

    def get_all_strategies(self) -> dict:
        """
        Get all the Python strategies created by the user on the AlgoBulls platform

        Returns:
            JSON Response received from AlgoBulls platform with list of all the created strategies.

        Info: ENDPOINT
            `OPTIONS` v2/user/strategy/build/python
        """
        endpoint = f'v2/user/strategy/build/python'
        response = self._send_request(endpoint=endpoint, method='options')
        return response

    def get_strategy_details(self, strategy_code: str) -> dict:
        """
        Get strategy details for

        Arguments:
            strategy_code: unique code of strategy, which is received while creating the strategy or

        Return:
            JSON

        Info: ENDPOINT
            `GET` v2/user/strategy/build/python
        """
        params = {'strategyCode': strategy_code}
        endpoint = f'v2/user/strategy/build/python'
        response = self._send_request(endpoint=endpoint, params=params)
        return response

    def search_instrument(self, instrument: str) -> dict:
        """

        Args:
            instrument: instrument key

        Returns:
            JSON Response


        Info: ENDPOINT
            `GET` v2/instrument/search
        """
        params = {'instrument': instrument}
        endpoint = f'v2/instrument/search'
        response = self._send_request(endpoint=endpoint, params=params, requires_authorization=False)
        return response

    def set_strategy_config(self, strategy_code: str, strategy_config: dict, trading_type: TradingType) -> (str, dict):
        """

        Args:
            strategy_code: strategy code
            strategy_config: strategy configuration
            trading_type: BACKTESTING, PAPER TRADING or REAL TRADING

        Returns:

        Info: ENDPOINT
           PATCH v2/portfolio/strategy
        """

        # Configure the params
        json_data = strategy_config
        key = self.__get_key(strategy_code=strategy_code, trading_type=trading_type)
        endpoint = f'v2/user/strategy/{key}/tweak'
        print('Setting Strategy Config...', end=' ')
        response = self._send_request(method='patch', endpoint=endpoint, json_data=json_data)
        print('Success.')
        return key, response

    def start_strategy_algotrading(self, strategy_code: str, trading_type: TradingType) -> dict:
        """
        Submit Backtesting / Paper Trading / Real Trading job for strategy with code strategy_code & return the job ID.

        Info: ENDPOINT
            `POST` v2/customer_strategy_algotrading
        """
        if trading_type == TradingType.REALTRADING:
            endpoint = 'v2/portfolio/strategies'
        elif trading_type == TradingType.PAPERTRADING:
            endpoint = 'v2/papertrading/strategies'
        elif trading_type == TradingType.BACKTESTING:
            endpoint = 'v2/backtesting/strategies'
        else:
            raise NotImplementedError

        try:
            key = self.__get_key(strategy_code=strategy_code, trading_type=trading_type)
            json_data = {'method': 'update', 'newVal': 1, 'key': key, 'record': {'status': 0}}
            print(f'Submitting {trading_type.name} job...', end=' ')
            response = self._send_request(method='post', endpoint=endpoint, json_data=json_data)
            print('Success.')
            return response
        except (AlgoBullsAPIForbiddenError, AlgoBullsAPIInsufficientBalanceError) as ex:
            print('Fail.')
            print(f'{ex.get_error_type()}: {ex.response}')

    def stop_strategy_algotrading(self, strategy_code: str, trading_type: TradingType) -> dict:
        """
        Stop Backtesting / Paper Trading / Real Trading job for strategy with code strategy_code & return the job ID.

        Info: ENDPOINT
            `POST` v1/customer_strategy_algotrading
        """
        if trading_type == TradingType.REALTRADING:
            endpoint = 'v2/portfolio/strategies'
        elif trading_type == TradingType.PAPERTRADING:
            endpoint = 'v2/papertrading/strategies'
        elif trading_type == TradingType.BACKTESTING:
            endpoint = 'v2/backtesting/strategies'
        else:
            raise NotImplementedError

        try:
            key = self.__get_key(strategy_code=strategy_code, trading_type=trading_type)
            json_data = {'method': 'update', 'newVal': 0, 'key': key, 'record': {'status': 2}}
            print(f'Stopping {trading_type.name} job...', end=' ')
            response = self._send_request(method='post', endpoint=endpoint, json_data=json_data)
            print('Success.')
            return response
        except (AlgoBullsAPIForbiddenError, AlgoBullsAPIInsufficientBalanceError) as ex:
            print('Fail.')
            print(f'{ex.get_error_type()}: {ex.response}')

    def get_job_status(self, strategy_code: str, trading_type: TradingType) -> dict:
        """


        Get status for a BACKTESTING/PAPERTRADING/REALTRADING Job

        Args:
            strategy_code: Strategy code
            trading_type: Trading type

        Returns:
            Job status

        Info: ENDPOINT
            `GET` v2/user/strategy/status
        """
        key = self.__get_key(strategy_code=strategy_code, trading_type=trading_type)
        params = {'key': key}
        endpoint = f'v2/user/strategy/status'
        response = self._send_request(endpoint=endpoint, params=params)
        return response

    def get_logs(self, strategy_code: str, trading_type: TradingType) -> dict:
        endpoint = 'v2/user/strategy/logs'
        key = self.__get_key(strategy_code=strategy_code, trading_type=trading_type)
        json_data = {'key': key}
        response = self._send_request(method='post', endpoint=endpoint, json_data=json_data)
        return response

    def get_reports(self, strategy_code: str, trading_type: TradingType, report_type: TradingReportType) -> dict:
        """
        Get reports for a BACKTESTING/PAPERTRADING/REALTRADING Job

        Args:
            strategy_code: Strategy code
            trading_type: Value of TradingType Enum
            report_type: Value of TradingReportType Enum

        Returns:
            Report data

        Info: ENDPOINT
            `GET` v1/customer_strategy_algotrading_reports
        """
        if report_type is TradingReportType.PNL_TABLE:
            endpoint = 'v2/user/strategy/pltable'
        elif report_type is TradingReportType.STATS_TABLE:
            endpoint = 'v2/user/strategy/statstable'
        elif report_type is TradingReportType.ORDER_HISTORY:
            endpoint = 'v2/user/strategy/orderhistory'
        else:
            raise NotImplementedError

        key = self.__get_key(strategy_code=strategy_code, trading_type=trading_type)
        params = {'key': key}
        response = self._send_request(endpoint=endpoint, params=params)
        return response
