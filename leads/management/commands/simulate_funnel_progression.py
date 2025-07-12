import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from leads.models import Lead, FunnelStageHistory


class Command(BaseCommand):
    help = 'Simulate leads progressing through the sales funnel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--percentage',
            type=int,
            default=20,
            help='Percentage of leads to move forward (default: 20%)',
        )

    def handle(self, *args, **options):
        percentage = options['percentage']
        
        self.stdout.write(f'Moving {percentage}% of leads forward in the funnel...')
        
        # Define progression rules
        progression_rules = {
            'form_submitted': {'next': 'meeting_booked', 'chance': 30},  # 30% chance
            'meeting_booked': {'next': 'meeting_held', 'chance': 70},   # 70% chance
            'meeting_held': {'next': 'pilot_signed', 'chance': 40},     # 40% chance  
            'pilot_signed': {'next': 'deal_closed', 'chance': 80},      # 80% chance
        }
        
        moved_count = 0
        total_processed = 0
        
        for current_stage, rules in progression_rules.items():
            # Get leads in this stage
            leads_in_stage = Lead.objects.filter(funnel_stage=current_stage)
            stage_count = leads_in_stage.count()
            
            if stage_count == 0:
                continue
                
            # Calculate how many to move based on percentage and chance
            base_move_count = int(stage_count * percentage / 100)
            chance_adjusted_count = int(base_move_count * rules['chance'] / 100)
            
            # Randomly select leads to move
            leads_to_move = random.sample(
                list(leads_in_stage), 
                min(chance_adjusted_count, stage_count)
            )
            
            for lead in leads_to_move:
                old_stage = lead.funnel_stage
                if lead.move_to_next_stage():
                    moved_count += 1
                    self.stdout.write(
                        f'  Moved {lead.full_name} from {old_stage} to {lead.funnel_stage}'
                    )
                    
            total_processed += len(leads_to_move)
            
            self.stdout.write(
                f'Stage {current_stage}: {len(leads_to_move)}/{stage_count} leads moved'
            )
        
        # Randomly churn some leads
        active_leads = Lead.objects.exclude(funnel_stage__in=['deal_closed', 'churned'])
        churn_count = int(active_leads.count() * 0.02)  # 2% churn rate
        
        if churn_count > 0:
            leads_to_churn = random.sample(list(active_leads), churn_count)
            for lead in leads_to_churn:
                old_stage = lead.funnel_stage
                lead.funnel_stage = 'churned'
                lead.churned_at = timezone.now()
                lead.save()
                
                FunnelStageHistory.objects.create(
                    lead=lead,
                    from_stage=old_stage,
                    to_stage='churned',
                    notes='Automatically churned by simulation'
                )
                
            self.stdout.write(f'Churned {churn_count} leads')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Funnel simulation complete:\n'
                f'- {moved_count} leads moved forward\n'
                f'- {churn_count} leads churned\n'
                f'- {total_processed} total leads processed'
            )
        )
