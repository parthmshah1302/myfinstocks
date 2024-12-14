import pandas as pd
from datetime import datetime
from typing import Dict, Any
import pdfkit
from services.portfolio_service import PortfolioService
from services.client_service import ClientService
import io

class ReportService:
    def __init__(self, db):
        self.db = db
        self.portfolio_service = PortfolioService(db)
        self.client_service = ClientService(db)
    
    def generate_portfolio_report(self, client_id: int) -> Dict[str, Any]:
        """Generate a comprehensive portfolio report"""
        # Get client information
        client_details = self.client_service.get_client_details(client_id)
        if client_details.empty:
            return None
        
        # Get portfolio summary
        summary = self.portfolio_service.get_portfolio_summary(client_id)
        
        # Get holdings with current prices
        holdings = self.portfolio_service.get_holdings_with_current_prices(client_id)
        
        # Generate HTML report
        report_html = self._generate_html_report(
            client_details.iloc[0],
            summary,
            holdings
        )
        
        # Generate PDF
        try:
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8"
            }
            pdf_data = pdfkit.from_string(report_html, False, options=pdf_options)
        except Exception as e:
            pdf_data = None
            
        return {
            "html": report_html,
            "pdf": pdf_data,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M")
        }
    
    def _generate_html_report(self, client_info, summary, holdings) -> str:
        """Generate HTML report content"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .summary-box {{ 
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                table {{ 
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{ 
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Portfolio Report</h1>
                <h2>{client_info['client_name']} - {client_info['family_name']}</h2>
                <p>Generated on: {datetime.now().strftime('%B %d, %Y %H:%M')}</p>
            </div>
            
            <div class="summary-box">
                <h3>Portfolio Summary</h3>
                <p>Total Portfolio Value: ₹{summary['current_value']:,.2f}</p>
                <p>Total Investment: ₹{summary['total_investment']:,.2f}</p>
                <p>Total Return: <span class="{'positive' if summary['return_percentage'] > 0 else 'negative'}">
                    {summary['return_percentage']:+.2f}%</span></p>
            </div>
            
            <h3>Holdings Details</h3>
            <table>
                <tr>
                    <th>Stock</th>
                    <th>Quantity</th>
                    <th>Buy Price</th>
                    <th>Current Price</th>
                    <th>Total Investment</th>
                    <th>Current Value</th>
                    <th>Return %</th>
                </tr>
                {''.join(f"""
                    <tr>
                        <td>{row['ticker'].replace('.NS', '')}</td>
                        <td>{row['quantity']}</td>
                        <td>₹{row['buy_price']:,.2f}</td>
                        <td>₹{row['current_price']:,.2f}</td>
                        <td>₹{row['total_investment']:,.2f}</td>
                        <td>₹{row['current_value']:,.2f}</td>
                        <td class="{'positive' if row['return_percentage'] > 0 else 'negative'}
                        <td class="{'positive' if row['return_percentage'] > 0 else 'negative'}">
                            {row['return_percentage']:+.2f}%</td>
                    </tr>
                """ for _, row in holdings.iterrows())}
            </table>
            
            <div style="margin-top: 40px;">
                <h3>Performance Analysis</h3>
                <p>Best Performing Stock: {holdings.loc[holdings['return_percentage'].idxmax(), 'ticker'].replace('.NS', '')} 
                   ({holdings['return_percentage'].max():+.2f}%)</p>
                <p>Worst Performing Stock: {holdings.loc[holdings['return_percentage'].idxmin(), 'ticker'].replace('.NS', '')} 
                   ({holdings['return_percentage'].min():+.2f}%)</p>
            </div>
            
            <div style="margin-top: 40px;">
                <p><em>Note: This report provides a snapshot of the portfolio at the time of generation. 
                Market values and returns are subject to change.</em></p>
                <p><em>Generated by Portfolio Management System</em></p>
            </div>
        </body>
        </html>
        """
    
    def generate_excel_report(self, client_id: int) -> bytes:
        """Generate an Excel report with multiple sheets"""
        # Get client information
        client_details = self.client_service.get_client_details(client_id)
        if client_details.empty:
            return None
        
        # Get portfolio data
        summary = self.portfolio_service.get_portfolio_summary(client_id)
        holdings = self.portfolio_service.get_holdings_with_current_prices(client_id)
        
        # Create Excel writer object
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Portfolio Summary Sheet
            summary_df = pd.DataFrame({
                'Metric': [
                    'Total Portfolio Value',
                    'Total Investment',
                    'Total Return',
                    'Return Percentage'
                ],
                'Value': [
                    f"₹{summary['current_value']:,.2f}",
                    f"₹{summary['total_investment']:,.2f}",
                    f"₹{summary['total_return']:,.2f}",
                    f"{summary['return_percentage']:+.2f}%"
                ]
            })
            summary_df.to_excel(writer, sheet_name='Portfolio Summary', index=False)
            
            # Holdings Details Sheet
            holdings.to_excel(writer, sheet_name='Holdings Details', index=False)
            
        return output.getvalue()