"""
Management command to score all leads based on ICP criteria using CVR API
"""
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from leads.models import Lead
from leads.services.cvr_scoring import default_scorer, CVRLeadScorer, ICPCriteria


class Command(BaseCommand):
    help = 'Score all leads based on ICP criteria using CVR API data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of leads to process in each batch (default: 50)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-scoring of all leads, even those already scored'
        )
        parser.add_argument(
            '--min-employees',
            type=int,
            default=200,
            help='Minimum employee count for ICP match (default: 200)'
        )
        parser.add_argument(
            '--industries',
            nargs='+',
            default=['FMCG', 'Retail', 'SaaS', 'Software', 'Technology'],
            help='Target industries for ICP matching'
        )
        parser.add_argument(
            '--cities',
            nargs='+',
            default=['Copenhagen', 'København', 'Aarhus', 'Århus'],
            help='Target cities for ICP matching'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be scored without actually scoring'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        force = options['force']
        dry_run = options['dry_run']
        
        # Create custom ICP criteria if provided
        icp_criteria = ICPCriteria(
            min_employees=options['min_employees'],
            target_industries=options['industries'],
            target_cities=options['cities']
        )
        
        # Create scorer with custom criteria
        scorer = CVRLeadScorer(icp_criteria)
        
        # Get leads to score
        if force:
            leads_query = Lead.objects.all()
            self.stdout.write(f"Force mode: Will score all {leads_query.count()} leads")
        else:
            # Only score leads that haven't been scored or have default score
            leads_query = Lead.objects.filter(Q(icp_score__lte=4) | Q(icp_score__isnull=True))
            self.stdout.write(f"Will score {leads_query.count()} unscored leads")
        
        if not leads_query.exists():
            self.stdout.write(
                self.style.SUCCESS('No leads need scoring!')
            )
            return
        
        # Show ICP criteria
        self.stdout.write(f"\nICP Criteria:")
        self.stdout.write(f"- Min employees: {icp_criteria.min_employees}")
        self.stdout.write(f"- Target industries: {', '.join(icp_criteria.target_industries)}")
        self.stdout.write(f"- Target cities: {', '.join(icp_criteria.target_cities)}")
        self.stdout.write(f"- Target employee levels: Manager+ positions")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nDRY RUN MODE - No leads will be updated')
            )
            # Show sample of leads that would be scored
            sample_leads = leads_query[:10]
            self.stdout.write("\nSample leads that would be scored:")
            for lead in sample_leads:
                self.stdout.write(f"- {lead.full_name} from {lead.company}")
            if leads_query.count() > 10:
                self.stdout.write(f"... and {leads_query.count() - 10} more")
            return
        
        # Process leads in batches
        total_leads = leads_query.count()
        processed = 0
        scored_count = 0
        error_count = 0
        
        self.stdout.write(f"\nProcessing {total_leads} leads in batches of {batch_size}...")
        
        for i in range(0, total_leads, batch_size):
            batch = list(leads_query[i:i + batch_size])
            batch_number = (i // batch_size) + 1
            
            self.stdout.write(f"\nProcessing batch {batch_number}: {len(batch)} leads")
            
            try:
                # Score the batch
                score_results = scorer.bulk_score_leads(batch)
                
                # Count successful scores
                batch_scored = sum(1 for result in score_results if result.total_score > 4)
                scored_count += batch_scored
                
                # Show progress
                processed += len(batch)
                progress = (processed / total_leads) * 100
                
                self.stdout.write(
                    f"Batch {batch_number} complete: {batch_scored}/{len(batch)} leads scored successfully"
                )
                self.stdout.write(f"Overall progress: {processed}/{total_leads} ({progress:.1f}%)")
                
                # Show some examples from this batch
                for lead, result in zip(batch[:3], score_results[:3]):
                    score_text = f"{result.total_score}/12"
                    if result.total_score >= 10:
                        score_style = self.style.SUCCESS(score_text)
                    elif result.total_score >= 7:
                        score_style = self.style.WARNING(score_text)
                    else:
                        score_style = score_text
                    
                    self.stdout.write(f"  • {lead.full_name} ({lead.company}): {score_style}")
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"Error processing batch {batch_number}: {e}")
                )
        
        # Final summary
        self.stdout.write(f"\n" + "="*50)
        self.stdout.write(f"SCORING COMPLETE")
        self.stdout.write(f"="*50)
        self.stdout.write(f"Total leads processed: {processed}")
        self.stdout.write(f"Successfully scored: {scored_count}")
        self.stdout.write(f"Errors: {error_count}")
        
        if scored_count > 0:
            success_rate = (scored_count / processed) * 100
            self.stdout.write(f"Success rate: {success_rate:.1f}%")
            
            # Show top scoring leads
            top_leads = Lead.objects.filter(icp_score__gte=10).order_by('-icp_score')[:5]
            if top_leads.exists():
                self.stdout.write(f"\nTop scoring leads:")
                for lead in top_leads:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"• {lead.full_name} ({lead.company}): {lead.icp_score}/12"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully completed lead scoring!')
        )
