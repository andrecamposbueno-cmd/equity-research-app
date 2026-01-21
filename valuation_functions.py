import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EquityValuation:
    def __init__(self, ticker, risk_free_rate=0.045, market_return=0.09):
        """
        Inicializa a classe de valuation
        
        Args:
            ticker (str): Símbolo do ativo
            risk_free_rate (float): Taxa livre de risco (default 4.5%)
            market_return (float): Retorno esperado do mercado (default 9%)
        """
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(ticker)
        self.risk_free_rate = risk_free_rate
        self.market_return = market_return
        self.data = None
        
    def get_financial_data(self, period="5y"):
        """
        Obtém dados financeiros históricos
        
        Args:
            period (str): Período dos dados (1y, 5y, 10y, max)
        """
        # Dados do preço
        self.price_data = self.stock.history(period=period)
        
        # Informações da empresa
        self.info = self.stock.info
        
        # Dados financeiros
        self.income_stmt = self.stock.financials
        self.balance_sheet = self.stock.balance_sheet
        self.cash_flow = self.stock.cashflow
        
        # Histórico de dividendos
        self.dividends = self.stock.dividends
        
        return self.price_data
    
    def calculate_financial_ratios(self):
        """
        Calcula os principais ratios financeiros
        """
        ratios = {}
        
        try:
            # Informações básicas
            ratios['current_price'] = self.info.get('currentPrice', np.nan)
            ratios['market_cap'] = self.info.get('marketCap', np.nan)
            ratios['shares_outstanding'] = self.info.get('sharesOutstanding', np.nan)
            
            # Profitability Ratios
            ratios['roe'] = self.info.get('returnOnEquity', np.nan) * 100
            ratios['roa'] = self.info.get('returnOnAssets', np.nan) * 100
            ratios['gross_margin'] = self.info.get('grossMargins', np.nan) * 100
            ratios['operating_margin'] = self.info.get('operatingMargins', np.nan) * 100
            ratios['profit_margin'] = self.info.get('profitMargins', np.nan) * 100
            
            # Valuation Ratios
            ratios['pe_ratio'] = self.info.get('trailingPE', np.nan)
            ratios['forward_pe'] = self.info.get('forwardPE', np.nan)
            ratios['pb_ratio'] = self.info.get('priceToBook', np.nan)
            ratios['ps_ratio'] = self.info.get('priceToSalesTrailing12Months', np.nan)
            ratios['ev_ebitda'] = self.info.get('enterpriseToEbitda', np.nan)
            ratios['ev_revenue'] = self.info.get('enterpriseToRevenue', np.nan)
            
            # Liquidity Ratios
            ratios['current_ratio'] = self.info.get('currentRatio', np.nan)
            ratios['quick_ratio'] = self.info.get('quickRatio', np.nan)
            
            # Debt Ratios
            ratios['debt_equity'] = self.info.get('debtToEquity', np.nan)
            ratios['debt_ebitda'] = self.info.get('debtToEbitda', np.nan)
            
            # Dividend Ratios
            ratios['dividend_yield'] = self.info.get('dividendYield', np.nan) * 100 if self.info.get('dividendYield') else 0
            ratios['payout_ratio'] = self.info.get('payoutRatio', np.nan) * 100
            
        except Exception as e:
            print(f"Erro ao calcular ratios: {e}")
            
        return ratios
    
    def calculate_beta(self, benchmark='^BVSP', period='3y'):
        """
        Calcula o beta do ativo em relação ao benchmark
        
        Args:
            benchmark (str): Índice de referência
            period (str): Período para cálculo
        """
        try:
            # Obtém dados do ativo e benchmark
            stock_returns = self.stock.history(period=period)['Close'].pct_change().dropna()
            bench = yf.Ticker(benchmark)
            bench_returns = bench.history(period=period)['Close'].pct_change().dropna()
            
            # Alinha as datas
            aligned_data = pd.concat([stock_returns, bench_returns], axis=1, join='inner')
            aligned_data.columns = ['stock', 'benchmark']
            
            # Calcula beta usando regressão linear
            beta, alpha, _, _, _ = stats.linregress(
                aligned_data['benchmark'].values, 
                aligned_data['stock'].values
            )
            
            return {
                'beta': beta,
                'alpha': alpha,
                'r_squared': beta**2 * (aligned_data['benchmark'].var() / aligned_data['stock'].var())
            }
        except:
            return {'beta': 1.0, 'alpha': 0, 'r_squared': 0}
    
    def calculate_wacc(self, beta, cost_of_debt=None, tax_rate=0.34):
        """
        Calcula o WACC (Custo Médio Ponderado de Capital)
        
        Args:
            beta (float): Beta do ativo
            cost_of_debt (float): Custo da dívida (se None, estima)
            tax_rate (float): Taxa de imposto corporativa
        """
        try:
            # CAPM para custo do equity
            cost_of_equity = self.risk_free_rate + beta * (self.market_return - self.risk_free_rate)
            
            # Se custo da dívida não fornecido, estima
            if cost_of_debt is None:
                interest_expense = self.info.get('interestExpense', 0)
                total_debt = self.info.get('totalDebt', 1)
                cost_of_debt = (interest_expense / total_debt) if total_debt > 0 else 0.06
            
            # Estrutura de capital
            market_cap = self.info.get('marketCap', 1)
            total_debt = self.info.get('totalDebt', 0)
            
            # Pesos
            equity_weight = market_cap / (market_cap + total_debt)
            debt_weight = total_debt / (market_cap + total_debt)
            
            # WACC
            wacc = (equity_weight * cost_of_equity + 
                   debt_weight * cost_of_debt * (1 - tax_rate))
            
            return {
                'wacc': wacc,
                'cost_of_equity': cost_of_equity,
                'cost_of_debt': cost_of_debt,
                'equity_weight': equity_weight,
                'debt_weight': debt_weight
            }
        except:
            return {'wacc': 0.09, 'cost_of_equity': 0.10, 'cost_of_debt': 0.06}
    
    def dcf_valuation(self, growth_rate=0.05, terminal_growth=0.03, years=5):
        """
        Realiza valuation pelo método DCF
        
        Args:
            growth_rate (float): Taxa de crescimento dos FCFF
            terminal_growth (float): Taxa de crescimento terminal
            years (int): Número de anos de projeção
        """
        try:
            # Obtém Free Cash Flow atual
            operating_cash_flow = self.cash_flow.loc['Operating Cash Flow', :].iloc[0]
            capital_expenditure = self.cash_flow.loc['Capital Expenditure', :].iloc[0]
            fcff = operating_cash_flow + capital_expenditure  # FCFF = OCF - Capex (Capex é negativo)
            
            # Calcula WACC
            beta_data = self.calculate_beta()
            wacc_data = self.calculate_wacc(beta_data['beta'])
            wacc = wacc_data['wacc']
            
            # Projeta FCFF
            fcff_projections = []
            for year in range(1, years + 1):
                fcff_projected = fcff * ((1 + growth_rate) ** year)
                fcff_projections.append(fcff_projected)
            
            # Calcula valor terminal
            terminal_fcff = fcff_projections[-1] * (1 + terminal_growth)
            terminal_value = terminal_fcff / (wacc - terminal_growth)
            
            # Desconta fluxos
            present_values = []
            for i, fcff_proj in enumerate(fcff_projections):
                pv = fcff_proj / ((1 + wacc) ** (i + 1))
                present_values.append(pv)
            
            pv_terminal = terminal_value / ((1 + wacc) ** years)
            
            # Valor da empresa
            enterprise_value = sum(present_values) + pv_terminal
            
            # Ajusta para valor do equity
            net_debt = self.info.get('totalDebt', 0) - self.info.get('cash', 0)
            equity_value = enterprise_value - net_debt
            
            # Valor por ação
            shares = self.info.get('sharesOutstanding', 1)
            intrinsic_value = equity_value / shares
            
            return {
                'intrinsic_value': intrinsic_value,
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'current_fcff': fcff,
                'wacc': wacc,
                'margin_of_safety': (intrinsic_value - self.info.get('currentPrice', 0)) / intrinsic_value * 100
            }
            
        except Exception as e:
            print(f"Erro no DCF: {e}")
            return None
    
    def comparable_companies_analysis(self, peers):
        """
        Análise de empresas comparáveis
        
        Args:
            peers (list): Lista de tickers de empresas comparáveis
        """
        peer_data = []
        
        for peer in peers:
            try:
                peer_stock = yf.Ticker(peer)
                peer_info = peer_stock.info
                
                peer_data.append({
                    'ticker': peer,
                    'market_cap': peer_info.get('marketCap', np.nan),
                    'pe_ratio': peer_info.get('trailingPE', np.nan),
                    'ev_ebitda': peer_info.get('enterpriseToEbitda', np.nan),
                    'pb_ratio': peer_info.get('priceToBook', np.nan),
                    'ps_ratio': peer_info.get('priceToSalesTrailing12Months', np.nan)
                })
            except:
                continue
        
        return pd.DataFrame(peer_data)
    
    def get_summary(self):
        """
        Retorna um resumo completo da análise
        """
        summary = {}
        
        # Informações básicas
        summary['company_name'] = self.info.get('longName', 'N/A')
        summary['sector'] = self.info.get('sector', 'N/A')
        summary['industry'] = self.info.get('industry', 'N/A')
        
        # Valuation DCF
        dcf_result = self.dcf_valuation()
        if dcf_result:
            summary.update(dcf_result)
        
        # Ratios
        ratios = self.calculate_financial_ratios()
        summary.update(ratios)
        
        # Beta
        beta_data = self.calculate_beta()
        summary.update(beta_data)
        
        # Recomendação
        current_price = self.info.get('currentPrice', 0)
        intrinsic_value = summary.get('intrinsic_value', 0)
        
        if intrinsic_value > 0:
            discount = ((intrinsic_value - current_price) / current_price) * 100
            summary['discount'] = discount
            
            if discount > 20:
                summary['recommendation'] = 'COMPRAR'
                summary['recommendation_color'] = 'green'
            elif discount > 10:
                summary['recommendation'] = 'ACUMULAR'
                summary['recommendation_color'] = 'lightgreen'
            elif discount < -20:
                summary['recommendation'] = 'VENDER'
                summary['recommendation_color'] = 'red'
            elif discount < -10:
                summary['recommendation'] = 'REDUZIR'
                summary['recommendation_color'] = 'orange'
            else:
                summary['recommendation'] = 'NEUTRO'
                summary['recommendation_color'] = 'yellow'
        
        return summary