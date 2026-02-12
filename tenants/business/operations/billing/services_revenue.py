import logging
from datetime import date
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from tenants.models import Tenant
from tenants.models.models_billing import RevenueEntry

logger = logging.getLogger(__name__)

class RevenueRecognitionService:
    """
    Chi Tier: Revenue Recognition (ASC 606) Service.
    Handles the amortization of revenue over time for financial compliance.
    """

    @staticmethod
    def recognize_subscription_payment(tenant: Tenant, total_amount: float, period_months: int = 12, start_date=None):
        """
        Amortizes a lump-sum payment (e.g., Annual Plan) into monthly revenue entries.
        Example: $1200 paid -> recognizes $100 every month for 12 months.
        """
        if not start_date:
            start_date = date.today()

        monthly_amount = Decimal(str(total_amount)) / Decimal(str(period_months))
        
        entries = []
        for i in range(period_months):
            reg_date = start_date + relativedelta(months=i)
            entry = RevenueEntry(
                tenant=tenant,
                amount=monthly_amount,
                recognized_date=reg_date,
                description=f"Amortized subscription revenue (Month {i+1}/{period_months})",
                source_type='subscription'
            )
            entries.append(entry)
        
        RevenueEntry.objects.bulk_create(entries)
        logger.info(f"Generated {period_months} revenue recognition entries for {tenant.slug}")

    @staticmethod
    def get_monthly_revenue_report(tenant: Tenant, year: int):
        """
        Returns summarized recognized revenue per month for a given year.
        """
        # In production, use aggregation for performance
        report = {}
        for month in range(1, 13):
            month_total = RevenueEntry.objects.filter(
                tenant=tenant,
                recognized_date__year=year,
                recognized_date__month=month
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            report[month] = float(month_total)
        return report
