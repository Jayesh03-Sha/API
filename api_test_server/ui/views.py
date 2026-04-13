from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from api_set1.models import (
    Lead, Deal, DealDocument,
    IndividualCustomer, CorporateCustomer, UBODetail,
    Transaction, InsurerReference, Attachment, StatusOverview,
    QuoteRequest, Quote, InsuranceProvider,
)


def home(request):
    context = {}
    if request.user.is_authenticated and request.user.is_staff:
        context = {
            'total_leads': Lead.objects.count(),
            'total_deals': Deal.objects.count(),
            'total_transactions': Transaction.objects.count(),
            'total_quotes': QuoteRequest.objects.count(),
            'total_providers': InsuranceProvider.objects.filter(is_active=True).count(),
        }
    return render(request, 'ui/home.html', context)


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    # --- Stats ---
    total_leads = Lead.objects.count()
    total_deals = Deal.objects.count()
    total_individual = IndividualCustomer.objects.count()
    total_corporate = CorporateCustomer.objects.count()
    total_transactions = Transaction.objects.count()
    total_quotes = QuoteRequest.objects.count()
    total_providers = InsuranceProvider.objects.filter(is_active=True).count()
    total_users = User.objects.count()

    # Revenue
    revenue = Transaction.objects.aggregate(
        total=Sum('customer_net_due')
    )['total'] or 0
    commission = Transaction.objects.aggregate(
        total=Sum('commission_amount')
    )['total'] or 0

    # Lead pipeline
    lead_stages = {}
    for stage_code, stage_label in Lead.STAGE_CHOICES:
        lead_stages[stage_label] = Lead.objects.filter(stage=stage_code).count()

    # Recent items
    recent_leads = Lead.objects.select_related('responsible').order_by('-created_at')[:5]
    recent_deals = Deal.objects.select_related('lead').order_by('-created_at')[:5]
    recent_transactions = Transaction.objects.select_related(
        'individual_customer', 'corporate_customer'
    ).order_by('-created_at')[:5]
    recent_quotes = Quote.objects.select_related('quote_request').order_by('-created_at')[:6]
    recent_statuses = StatusOverview.objects.select_related(
        'transaction', 'user', 'assigned_user'
    ).order_by('-date')[:8]

    # Provider performance summary
    provider_stats_raw = Quote.objects.values('provider').annotate(
        total_quotes=Count('id'),
        best_quotes=Count('id', filter=Q(is_best=True)),
        avg_premium=Avg('premium'),
        avg_score=Avg('comparison_score')
    ).order_by('-total_quotes')

    provider_name_map = dict(Quote.PROVIDER_CHOICES)
    provider_performance = [
        {
            'provider': item['provider'],
            'provider_name': provider_name_map.get(item['provider'], item['provider']),
            'total_quotes': item['total_quotes'],
            'best_quotes': item['best_quotes'],
            'avg_premium': item['avg_premium'] or 0,
            'avg_score': item['avg_score'] or 0,
        }
        for item in provider_stats_raw
    ]

    # Product type distribution
    product_distribution = Lead.objects.values('product_type').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'total_leads': total_leads,
        'total_deals': total_deals,
        'total_individual': total_individual,
        'total_corporate': total_corporate,
        'total_transactions': total_transactions,
        'total_quotes': total_quotes,
        'total_providers': total_providers,
        'total_users': total_users,
        'recent_quotes': recent_quotes,
        'provider_performance': provider_performance,
        'revenue': revenue,
        'commission': commission,
        'lead_stages': lead_stages,
        'recent_leads': recent_leads,
        'recent_deals': recent_deals,
        'recent_transactions': recent_transactions,
        'recent_statuses': recent_statuses,
        'product_distribution': product_distribution,
    }
    return render(request, 'ui/admin_dashboard.html', context)


@login_required
def lead_detail(request, lead_id):
    """Detail view for a single Lead — CRM style"""
    if not request.user.is_staff:
        return redirect('home')

    lead = get_object_or_404(Lead.objects.select_related('responsible'), pk=lead_id)
    deals = lead.deals.all().order_by('-created_at')
    all_leads = Lead.objects.order_by('-created_at')[:20]

    # Stage pipeline data
    stages = Lead.STAGE_CHOICES
    current_stage_index = next(
        (i for i, (code, _) in enumerate(stages) if code == lead.stage), 0
    )

    context = {
        'lead': lead,
        'deals': deals,
        'stages': stages,
        'current_stage_index': current_stage_index,
        'all_leads': all_leads,
    }
    return render(request, 'ui/lead_detail.html', context)


@login_required
def deal_detail(request, deal_id):
    """Detail view for a single Deal"""
    if not request.user.is_staff:
        return redirect('home')

    deal = get_object_or_404(
        Deal.objects.select_related('lead'), pk=deal_id
    )
    documents = deal.documents.all().order_by('-uploaded_at')

    context = {
        'deal': deal,
        'documents': documents,
    }
    return render(request, 'ui/deal_detail.html', context)


@login_required
def transaction_detail(request, txn_id):
    """Detail view for a single Transaction"""
    if not request.user.is_staff:
        return redirect('home')

    txn = get_object_or_404(
        Transaction.objects.select_related(
            'individual_customer', 'corporate_customer'
        ), pk=txn_id
    )
    insurer_ref = InsurerReference.objects.filter(transaction=txn).first()
    attachments = txn.attachments.all().order_by('-uploaded_at')
    statuses = txn.status_history.select_related('user', 'assigned_user').order_by('-date')

    context = {
        'txn': txn,
        'insurer_ref': insurer_ref,
        'attachments': attachments,
        'statuses': statuses,
    }
    return render(request, 'ui/transaction_detail.html', context)


@login_required
def leads_list(request):
    """List all leads"""
    if not request.user.is_staff:
        return redirect('home')
    leads = Lead.objects.select_related('responsible').order_by('-created_at')
    context = {'leads': leads, 'stages': Lead.STAGE_CHOICES}
    return render(request, 'ui/leads_list.html', context)


@login_required
def deals_list(request):
    """List all deals"""
    if not request.user.is_staff:
        return redirect('home')
    deals = Deal.objects.select_related('lead').order_by('-created_at')
    context = {'deals': deals}
    return render(request, 'ui/deals_list.html', context)


@login_required
def transactions_list(request):
    """List all transactions"""
    if not request.user.is_staff:
        return redirect('home')
    transactions = Transaction.objects.select_related(
        'individual_customer', 'corporate_customer'
    ).order_by('-created_at')
    context = {'transactions': transactions}
    return render(request, 'ui/transactions_list.html', context)


@login_required
def customers_list(request):
    """List all customers (individual + corporate)"""
    if not request.user.is_staff:
        return redirect('home')
    individuals = IndividualCustomer.objects.order_by('-created_at')
    corporates = CorporateCustomer.objects.order_by('-created_at')
    context = {'individuals': individuals, 'corporates': corporates}
    return render(request, 'ui/customers_list.html', context)
@login_required
def quote_proposal(request, quote_request_id):
    """
    Renders a high-fidelity professional proposal for a specific quote request.
    Includes branding, comparison table, and membership marketing.
    """
    if not request.user.is_staff:
        return redirect('home')
        
    quote_request = get_object_or_404(
        QuoteRequest.objects.select_related('user'), 
        pk=quote_request_id
    )
    # Get all quotes for this request, sorted by best score
    quotes = Quote.objects.filter(quote_request=quote_request).order_by('-comparison_score')
    
    if not quotes.exists():
        messages.warning(request, "No quotes found for this request. Please fetch quotes first.")
        return redirect('admin_dashboard')
        
    best_quote = quotes.filter(is_best=True).first()
    
    context = {
        'quote_request': quote_request,
        'quotes': quotes,
        'best_quote': best_quote,
        'marketing': True # To toggle second page optionally
    }
    
    return render(request, 'ui/proposal.html', context)


# --- Public Portal Views ---

def portal_index(request):
    """Public landing page for Promise Insurance"""
    return render(request, 'ui/portal_index.html')


@login_required
def portal_quote_request(request):
    """Step 1: Multi-step quote request form"""
    return render(request, 'ui/portal_quote_request.html')


@login_required
def portal_comparison(request, quote_request_id):
    """Step 2: Comparison results matrix"""
    quote_request = get_object_or_404(QuoteRequest, pk=quote_request_id, user=request.user)
    quotes = quote_request.quotes.all().order_by('-comparison_score')
    best_quote = quotes.filter(is_best=True).first()
    
    # Calculate some summary stats
    avg_premium = quotes.aggregate(avg=Sum('premium'))['avg'] or 0
    if quotes.count() > 0:
        avg_premium = avg_premium / quotes.count()
        
    context = {
        'quote_request': quote_request,
        'all_quotes': quotes,
        'best_quote': best_quote,
        'summary': {
            'avg_premium': avg_premium,
            'count': quotes.count()
        }
    }
    return render(request, 'ui/portal_comparison.html', context)
