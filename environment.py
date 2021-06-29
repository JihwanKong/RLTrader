class Environment:
    # 종가 column -> 4번째
    PRICE_IDX = 4

    def __init__(self, chart_data=None):
        self.chart_data = chart_data
        self.observation = None
        self.idx = -1

    # reset(): idx observation 초기화
    def reset(self):
        self.observation = None
        self.idx = -1

    # observe(): idx를 다음 위치로 이동하고 obaservation을 업데이트
    def observe(self):
        if len(self.chart_data) > self.idx + 1:
            self.idx += 1
            # pandas dataframe을 사용하므로 iloc으로 row 위치 파악
            self.observation = self.chart_data.iloc[self.idx]
            return self.observation
        return None

    # get_price(): 현재 observation에서 종가 획득
    def get_price(self):
        if self.observation is not None:
            return self.observation[self.PRICE_IDX]
        return None

    def set_chart_data(self, chart_data):
        self.chart_data = chart_data
