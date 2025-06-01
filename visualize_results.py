#!/usr/bin/env python3
"""
Visualization script for ModaMesh™ simulation results
Creates comprehensive visualizations of simulation outcomes including financial metrics,
partnership dynamics, and strategic insights.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class SimulationVisualizer:
    def __init__(self, analysis_file: str = None):
        """Initialize visualizer with latest analysis file if not specified"""
        if analysis_file is None:
            # Find the latest analysis file
            results_dir = Path("simulation_results")
            analysis_files = list(results_dir.glob("single_model_analysis_*.json"))
            if not analysis_files:
                raise FileNotFoundError("No analysis files found in simulation_results/")
            self.analysis_file = sorted(analysis_files)[-1]
        else:
            self.analysis_file = Path(analysis_file)
        
        # Load analysis data
        with open(self.analysis_file, 'r') as f:
            self.analysis = json.load(f)
        
        # Extract timestamp for saving
        self.timestamp = self.analysis_file.stem.split('_')[-1]
        
    def create_all_visualizations(self):
        """Generate all visualizations and save them"""
        print(f"📊 Creating visualizations for {self.analysis_file.name}...")
        
        # Create a comprehensive figure with multiple subplots
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Revenue & Profit Comparison
        self._plot_financial_comparison(fig)
        
        # 2. Profit Margins
        self._plot_profit_margins(fig)
        
        # 3. NPV Analysis
        self._plot_npv_analysis(fig)
        
        # 4. Capacity Utilization
        self._plot_capacity_utilization(fig)
        
        # 5. Partnership Analysis
        self._plot_partnership_analysis(fig)
        
        # 6. Risk-Return Profile
        self._plot_risk_return(fig)
        
        # 7. Revenue Distribution
        self._plot_revenue_distribution(fig)
        
        # 8. Profit Distribution
        self._plot_profit_distribution(fig)
        
        # 9. Key Metrics Summary
        self._plot_metrics_summary(fig)
        
        # Save the comprehensive visualization
        plt.tight_layout()
        output_path = Path("simulation_results") / f"comprehensive_analysis_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved comprehensive analysis to {output_path}")
        
        # Create individual focused charts
        self._create_executive_summary()
        self._create_financial_breakdown()
        self._create_strategic_insights()
        
        plt.close('all')
        
    def _plot_financial_comparison(self, fig):
        """Plot revenue and profit comparison"""
        ax = fig.add_subplot(4, 3, 1)
        
        models = ['Co-Branded', 'White-Label']
        revenues = [
            self.analysis['co-branded']['mean_total_revenue'] / 1_000_000,
            self.analysis['white-label']['mean_total_revenue'] / 1_000_000
        ]
        profits = [
            self.analysis['co-branded']['mean_total_profit'] / 1_000_000,
            self.analysis['white-label']['mean_total_profit'] / 1_000_000
        ]
        
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, revenues, width, label='Revenue', color='skyblue')
        bars2 = ax.bar(x + width/2, profits, width, label='Profit', color='lightgreen')
        
        ax.set_ylabel('EUR (Millions)')
        ax.set_title('5-Year Revenue vs Profit Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'€{height:.1f}M',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
    
    def _plot_profit_margins(self, fig):
        """Plot profit margin comparison"""
        ax = fig.add_subplot(4, 3, 2)
        
        models = ['Co-Branded', 'White-Label']
        margins = [
            (self.analysis['co-branded']['mean_total_profit'] / 
             self.analysis['co-branded']['mean_total_revenue']) * 100,
            (self.analysis['white-label']['mean_total_profit'] / 
             self.analysis['white-label']['mean_total_revenue']) * 100
        ]
        
        bars = ax.bar(models, margins, color=['darkgreen', 'orange'])
        ax.set_ylabel('Profit Margin (%)')
        ax.set_title('Profit Margin Comparison')
        ax.set_ylim(0, max(margins) * 1.2)
        
        # Add value labels
        for bar, margin in zip(bars, margins):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'{margin:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    def _plot_npv_analysis(self, fig):
        """Plot NPV comparison with R&D recovery"""
        ax = fig.add_subplot(4, 3, 3)
        
        rd_investment = 5.77  # €5.77M
        
        cb_npv = self.analysis['co-branded']['mean_npv_profit'] / 1_000_000
        wl_npv = self.analysis['white-label']['mean_npv_profit'] / 1_000_000
        
        models = ['Co-Branded', 'White-Label']
        npvs = [cb_npv, wl_npv]
        
        bars = ax.bar(models, npvs, color=['purple', 'coral'])
        
        # Add R&D investment line
        ax.axhline(y=rd_investment, color='red', linestyle='--', label='R&D Investment')
        
        ax.set_ylabel('NPV (EUR Millions)')
        ax.set_title('NPV Analysis vs R&D Investment')
        ax.legend()
        
        # Add value labels and R&D recovery %
        for bar, npv in zip(bars, npvs):
            recovery = (npv / rd_investment) * 100
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                   f'€{npv:.1f}M\n({recovery:.0f}% R&D recovery)',
                   ha='center', va='bottom')
    
    def _plot_capacity_utilization(self, fig):
        """Plot capacity utilization analysis"""
        ax = fig.add_subplot(4, 3, 4)
        
        models = ['Co-Branded', 'White-Label']
        utilization = [
            self.analysis['co-branded']['avg_capacity_utilization'],
            self.analysis['white-label']['avg_capacity_utilization']
        ]
        
        # Create pie charts showing utilized vs available capacity
        for i, (model, util) in enumerate(zip(models, utilization)):
            ax_sub = fig.add_subplot(4, 6, 13 + i)
            sizes = [util, 100 - util]
            colors = ['#ff9999', '#66b3ff']
            labels = ['Utilized', 'Available']
            
            wedges, texts, autotexts = ax_sub.pie(sizes, labels=labels, colors=colors,
                                                   autopct='%1.1f%%', startangle=90)
            ax_sub.set_title(f'{model}\nCapacity Usage')
    
    def _plot_partnership_analysis(self, fig):
        """Plot partnership metrics"""
        ax = fig.add_subplot(4, 3, 5)
        
        models = ['Co-Branded', 'White-Label']
        partnerships = [
            self.analysis['co-branded']['mean_partnerships'],
            self.analysis['white-label']['mean_partnerships']
        ]
        rejected = [
            self.analysis['co-branded']['mean_rejected_capacity'],
            self.analysis['white-label']['mean_rejected_capacity']
        ]
        
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, partnerships, width, label='Formed', color='green')
        bars2 = ax.bar(x + width/2, rejected, width, label='Rejected (Capacity)', color='red')
        
        ax.set_ylabel('Number of Partnerships')
        ax.set_title('Partnership Formation Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
    
    def _plot_risk_return(self, fig):
        """Plot risk-return profile"""
        ax = fig.add_subplot(4, 3, 6)
        
        # Use coefficient of variation as risk metric
        cb_risk = (self.analysis['co-branded']['std_total_profit'] / 
                   self.analysis['co-branded']['mean_total_profit']) * 100
        wl_risk = (self.analysis['white-label']['std_total_profit'] / 
                   self.analysis['white-label']['mean_total_profit']) * 100
        
        cb_return = self.analysis['co-branded']['mean_npv_profit'] / 1_000_000
        wl_return = self.analysis['white-label']['mean_npv_profit'] / 1_000_000
        
        ax.scatter(cb_risk, cb_return, s=200, c='darkgreen', label='Co-Branded', marker='o')
        ax.scatter(wl_risk, wl_return, s=200, c='orange', label='White-Label', marker='s')
        
        ax.set_xlabel('Risk (Coefficient of Variation %)')
        ax.set_ylabel('Return (NPV in €M)')
        ax.set_title('Risk-Return Profile')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add annotations
        ax.annotate('Co-Branded\n(Lower Risk,\nHigher Return)', 
                   xy=(cb_risk, cb_return), xytext=(cb_risk-2, cb_return+0.5),
                   arrowprops=dict(arrowstyle='->', color='black', alpha=0.5))
        ax.annotate('White-Label\n(Higher Risk,\nLower Return)', 
                   xy=(wl_risk, wl_return), xytext=(wl_risk+1, wl_return-0.5),
                   arrowprops=dict(arrowstyle='->', color='black', alpha=0.5))
    
    def _plot_revenue_distribution(self, fig):
        """Plot revenue distribution percentiles"""
        ax = fig.add_subplot(4, 3, 7)
        
        percentiles = ['5%', '25%', '50%', '75%', '95%']
        cb_values = [self.analysis['co-branded']['revenue_percentiles'][p] / 1_000_000 
                     for p in percentiles]
        wl_values = [self.analysis['white-label']['revenue_percentiles'][p] / 1_000_000 
                     for p in percentiles]
        
        x = np.arange(len(percentiles))
        width = 0.35
        
        ax.bar(x - width/2, cb_values, width, label='Co-Branded', color='darkgreen')
        ax.bar(x + width/2, wl_values, width, label='White-Label', color='orange')
        
        ax.set_xlabel('Percentile')
        ax.set_ylabel('Revenue (EUR Millions)')
        ax.set_title('Revenue Distribution Across Percentiles')
        ax.set_xticks(x)
        ax.set_xticklabels(percentiles)
        ax.legend()
    
    def _plot_profit_distribution(self, fig):
        """Plot profit distribution percentiles"""
        ax = fig.add_subplot(4, 3, 8)
        
        percentiles = ['5%', '25%', '50%', '75%', '95%']
        cb_values = [self.analysis['co-branded']['profit_percentiles'][p] / 1_000_000 
                     for p in percentiles]
        wl_values = [self.analysis['white-label']['profit_percentiles'][p] / 1_000_000 
                     for p in percentiles]
        
        x = np.arange(len(percentiles))
        width = 0.35
        
        ax.bar(x - width/2, cb_values, width, label='Co-Branded', color='darkgreen')
        ax.bar(x + width/2, wl_values, width, label='White-Label', color='orange')
        
        ax.set_xlabel('Percentile')
        ax.set_ylabel('Profit (EUR Millions)')
        ax.set_title('Profit Distribution Across Percentiles')
        ax.set_xticks(x)
        ax.set_xticklabels(percentiles)
        ax.legend()
    
    def _plot_metrics_summary(self, fig):
        """Plot key metrics summary table"""
        ax = fig.add_subplot(4, 3, 9)
        ax.axis('off')
        
        # Create summary data
        metrics = [
            ['Metric', 'Co-Branded', 'White-Label', 'Winner'],
            ['Revenue (€M)', 
             f"{self.analysis['co-branded']['mean_total_revenue']/1e6:.1f}",
             f"{self.analysis['white-label']['mean_total_revenue']/1e6:.1f}",
             'White-Label (2.1x)'],
            ['Profit (€M)', 
             f"{self.analysis['co-branded']['mean_total_profit']/1e6:.1f}",
             f"{self.analysis['white-label']['mean_total_profit']/1e6:.1f}",
             'Co-Branded (1.8x)'],
            ['Profit Margin', 
             f"{(self.analysis['co-branded']['mean_total_profit']/self.analysis['co-branded']['mean_total_revenue']*100):.1f}%",
             f"{(self.analysis['white-label']['mean_total_profit']/self.analysis['white-label']['mean_total_revenue']*100):.1f}%",
             'Co-Branded'],
            ['NPV (€M)', 
             f"{self.analysis['co-branded']['mean_npv_profit']/1e6:.1f}",
             f"{self.analysis['white-label']['mean_npv_profit']/1e6:.1f}",
             'Co-Branded'],
            ['Partnerships', 
             f"{self.analysis['co-branded']['mean_partnerships']:.0f}",
             f"{self.analysis['white-label']['mean_partnerships']:.0f}",
             'White-Label'],
            ['Capacity Used', 
             f"{self.analysis['co-branded']['avg_capacity_utilization']:.1f}%",
             f"{self.analysis['white-label']['avg_capacity_utilization']:.1f}%",
             'White-Label'],
            ['R&D Recovery', 
             f"{(self.analysis['co-branded']['mean_total_profit']/5.77e6*100):.0f}%",
             f"{(self.analysis['white-label']['mean_total_profit']/5.77e6*100):.0f}%",
             'Co-Branded']
        ]
        
        # Create table
        table = ax.table(cellText=metrics, cellLoc='center', loc='center',
                        colWidths=[0.25, 0.25, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header row
        for i in range(4):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Highlight winner cells
        winner_color = '#90EE90'
        table[(2, 3)].set_facecolor(winner_color)  # Profit winner
        table[(3, 3)].set_facecolor(winner_color)  # Margin winner
        table[(4, 3)].set_facecolor(winner_color)  # NPV winner
        table[(7, 3)].set_facecolor(winner_color)  # R&D Recovery winner
        
        ax.set_title('Key Metrics Summary', fontsize=14, fontweight='bold', pad=20)
    
    def _create_executive_summary(self):
        """Create executive summary visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Revenue vs Profit bars
        models = ['Co-Branded', 'White-Label']
        revenues = [self.analysis['co-branded']['mean_total_revenue'] / 1_000_000,
                   self.analysis['white-label']['mean_total_revenue'] / 1_000_000]
        profits = [self.analysis['co-branded']['mean_total_profit'] / 1_000_000,
                  self.analysis['white-label']['mean_total_profit'] / 1_000_000]
        
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, revenues, width, label='Revenue', color='#3498db')
        bars2 = ax1.bar(x + width/2, profits, width, label='Profit', color='#2ecc71')
        
        ax1.set_ylabel('EUR (Millions)', fontsize=12)
        ax1.set_title('5-Year Financial Performance', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(models)
        ax1.legend()
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2, height + 1,
                        f'€{height:.1f}M', ha='center', va='bottom')
        
        # 2. Profit margins donut chart
        margins = [(self.analysis['co-branded']['mean_total_profit'] / 
                   self.analysis['co-branded']['mean_total_revenue']) * 100,
                  (self.analysis['white-label']['mean_total_profit'] / 
                   self.analysis['white-label']['mean_total_revenue']) * 100]
        
        colors = ['#2ecc71', '#e74c3c']
        wedges, texts, autotexts = ax2.pie(margins, labels=models, colors=colors,
                                           autopct='%1.1f%%', startangle=90,
                                           pctdistance=0.85)
        
        # Create donut
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax2.add_artist(centre_circle)
        ax2.set_title('Profit Margin Comparison', fontsize=14, fontweight='bold')
        
        # 3. NPV with R&D recovery
        cb_npv = self.analysis['co-branded']['mean_npv_profit'] / 1_000_000
        wl_npv = self.analysis['white-label']['mean_npv_profit'] / 1_000_000
        rd_investment = 5.77
        
        npvs = [cb_npv, wl_npv]
        colors = ['#9b59b6', '#f39c12']
        bars = ax3.bar(models, npvs, color=colors)
        
        ax3.axhline(y=rd_investment, color='red', linestyle='--', 
                   label=f'R&D Investment (€{rd_investment}M)')
        ax3.set_ylabel('NPV (EUR Millions)', fontsize=12)
        ax3.set_title('NPV Analysis & R&D Recovery', fontsize=14, fontweight='bold')
        ax3.legend()
        
        for bar, npv in zip(bars, npvs):
            recovery = (npv / rd_investment) * 100
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f'€{npv:.1f}M\n({recovery:.0f}% recovery)',
                    ha='center', va='bottom')
        
        # 4. Strategic positioning
        ax4.axis('off')
        
        # Winner indicator
        winner = self.analysis['recommendation']['chosen_model'].replace('-', ' ').title()
        score_diff = self.analysis['recommendation']['score_difference_pct']
        
        ax4.text(0.5, 0.9, f'RECOMMENDED MODEL: {winner}', 
                ha='center', va='top', fontsize=20, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen'))
        
        ax4.text(0.5, 0.7, f'{score_diff:.1f}% better NPV performance',
                ha='center', va='top', fontsize=14)
        
        # Key insights
        insights = [
            f"• Co-Branded: Higher margins ({margins[0]:.1f}%), lower volume",
            f"• White-Label: Higher volume ({self.analysis['comparison']['revenue_ratio']:.1f}x), lower margins",
            f"• Co-Branded delivers {1/self.analysis['comparison']['profit_ratio']:.1f}x more profit",
            f"• Capacity headroom: CB {100-self.analysis['co-branded']['avg_capacity_utilization']:.0f}%, WL {100-self.analysis['white-label']['avg_capacity_utilization']:.0f}%"
        ]
        
        for i, insight in enumerate(insights):
            ax4.text(0.1, 0.5 - i*0.1, insight, ha='left', va='top', fontsize=12)
        
        plt.tight_layout()
        output_path = Path("simulation_results") / f"executive_summary_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved executive summary to {output_path}")
        plt.close()
    
    def _create_financial_breakdown(self):
        """Create detailed financial breakdown"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Calculate margins for later use
        cb_margin = (self.analysis['co-branded']['mean_total_profit'] / 
                     self.analysis['co-branded']['mean_total_revenue']) * 100
        wl_margin = (self.analysis['white-label']['mean_total_profit'] / 
                     self.analysis['white-label']['mean_total_revenue']) * 100
        margins = [cb_margin, wl_margin]
        
        # 1. Revenue range (box plot style)
        ax = axes[0, 0]
        
        cb_revenue_data = [
            self.analysis['co-branded']['revenue_percentiles']['5%'] / 1_000_000,
            self.analysis['co-branded']['revenue_percentiles']['25%'] / 1_000_000,
            self.analysis['co-branded']['revenue_percentiles']['50%'] / 1_000_000,
            self.analysis['co-branded']['revenue_percentiles']['75%'] / 1_000_000,
            self.analysis['co-branded']['revenue_percentiles']['95%'] / 1_000_000,
        ]
        
        wl_revenue_data = [
            self.analysis['white-label']['revenue_percentiles']['5%'] / 1_000_000,
            self.analysis['white-label']['revenue_percentiles']['25%'] / 1_000_000,
            self.analysis['white-label']['revenue_percentiles']['50%'] / 1_000_000,
            self.analysis['white-label']['revenue_percentiles']['75%'] / 1_000_000,
            self.analysis['white-label']['revenue_percentiles']['95%'] / 1_000_000,
        ]
        
        positions = [1, 2]
        bp = ax.boxplot([cb_revenue_data, wl_revenue_data], positions=positions,
                       widths=0.6, patch_artist=True, showmeans=True)
        
        colors = ['lightgreen', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_xticklabels(['Co-Branded', 'White-Label'])
        ax.set_ylabel('Revenue (EUR Millions)')
        ax.set_title('Revenue Distribution (5-Year Total)')
        ax.grid(True, alpha=0.3)
        
        # 2. Profit range
        ax = axes[0, 1]
        
        cb_profit_data = [
            self.analysis['co-branded']['profit_percentiles']['5%'] / 1_000_000,
            self.analysis['co-branded']['profit_percentiles']['25%'] / 1_000_000,
            self.analysis['co-branded']['profit_percentiles']['50%'] / 1_000_000,
            self.analysis['co-branded']['profit_percentiles']['75%'] / 1_000_000,
            self.analysis['co-branded']['profit_percentiles']['95%'] / 1_000_000,
        ]
        
        wl_profit_data = [
            self.analysis['white-label']['profit_percentiles']['5%'] / 1_000_000,
            self.analysis['white-label']['profit_percentiles']['25%'] / 1_000_000,
            self.analysis['white-label']['profit_percentiles']['50%'] / 1_000_000,
            self.analysis['white-label']['profit_percentiles']['75%'] / 1_000_000,
            self.analysis['white-label']['profit_percentiles']['95%'] / 1_000_000,
        ]
        
        bp = ax.boxplot([cb_profit_data, wl_profit_data], positions=positions,
                       widths=0.6, patch_artist=True, showmeans=True)
        
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_xticklabels(['Co-Branded', 'White-Label'])
        ax.set_ylabel('Profit (EUR Millions)')
        ax.set_title('Profit Distribution (5-Year Total)')
        ax.grid(True, alpha=0.3)
        
        # 3. Unit economics
        ax = axes[1, 0]
        
        # Calculate average units and profit per unit
        cb_units = self.analysis['co-branded']['mean_partnerships'] * 25000  # Estimated avg units
        wl_units = self.analysis['white-label']['mean_partnerships'] * 50000  # Estimated avg units
        
        cb_profit_per_unit = self.analysis['co-branded']['mean_total_profit'] / cb_units
        wl_profit_per_unit = self.analysis['white-label']['mean_total_profit'] / wl_units
        
        models = ['Co-Branded', 'White-Label']
        profit_per_unit = [cb_profit_per_unit, wl_profit_per_unit]
        
        bars = ax.bar(models, profit_per_unit, color=['darkgreen', 'darkorange'])
        ax.set_ylabel('Profit per Unit (EUR)')
        ax.set_title('Unit Economics Comparison')
        
        for bar, value in zip(bars, profit_per_unit):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'€{value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Financial ratios
        ax = axes[1, 1]
        
        ratios = ['Revenue\nRatio', 'Profit\nRatio', 'NPV\nRatio', 'Margin\nRatio']
        values = [
            self.analysis['comparison']['revenue_ratio'],
            self.analysis['comparison']['profit_ratio'],
            self.analysis['comparison']['npv_profit_ratio'],
            (margins[0] / margins[1])  # CB margin / WL margin
        ]
        
        bars = ax.bar(ratios, values, color=['blue', 'green', 'purple', 'orange'])
        ax.axhline(y=1, color='red', linestyle='--', label='Parity')
        ax.set_ylabel('Ratio (White-Label / Co-Branded)')
        ax.set_title('Performance Ratios')
        ax.legend()
        
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                   f'{value:.2f}x', ha='center', va='bottom')
        
        plt.tight_layout()
        output_path = Path("simulation_results") / f"financial_breakdown_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved financial breakdown to {output_path}")
        plt.close()
    
    def _create_strategic_insights(self):
        """Create strategic insights visualization"""
        fig = plt.figure(figsize=(14, 10))
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Strategic positioning matrix
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        
        # Position models on strategic grid
        cb_margin = (self.analysis['co-branded']['mean_total_profit'] / 
                    self.analysis['co-branded']['mean_total_revenue']) * 100
        wl_margin = (self.analysis['white-label']['mean_total_profit'] / 
                    self.analysis['white-label']['mean_total_revenue']) * 100
        
        cb_volume = self.analysis['co-branded']['mean_partnerships'] * 25000 / 1_000_000
        wl_volume = self.analysis['white-label']['mean_partnerships'] * 50000 / 1_000_000
        
        ax1.scatter(cb_volume, cb_margin, s=500, c='darkgreen', marker='o', 
                   label='Co-Branded', edgecolors='black', linewidth=2)
        ax1.scatter(wl_volume, wl_margin, s=500, c='darkorange', marker='s', 
                   label='White-Label', edgecolors='black', linewidth=2)
        
        ax1.set_xlabel('Volume (Million Units)', fontsize=12)
        ax1.set_ylabel('Profit Margin (%)', fontsize=12)
        ax1.set_title('Strategic Positioning Matrix', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add quadrant labels
        ax1.text(0.5, 25, 'Niche\nPremium', ha='center', va='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.5))
        ax1.text(2, 5, 'Mass\nMarket', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.5))
        
        # 2. Capacity efficiency gauge
        ax2 = fig.add_subplot(gs[0, 2])
        
        cb_util = self.analysis['co-branded']['avg_capacity_utilization']
        wl_util = self.analysis['white-label']['avg_capacity_utilization']
        
        categories = ['Co-Branded', 'White-Label']
        utilizations = [cb_util, wl_util]
        
        bars = ax2.barh(categories, utilizations, color=['green', 'orange'])
        ax2.set_xlim(0, 100)
        ax2.set_xlabel('Capacity Utilization (%)')
        ax2.set_title('Production Efficiency')
        
        for bar, util in zip(bars, utilizations):
            ax2.text(util + 2, bar.get_y() + bar.get_height()/2,
                    f'{util:.1f}%', va='center')
        
        # 3. Growth potential
        ax3 = fig.add_subplot(gs[1, 2])
        
        growth_potential = [100 - cb_util, 100 - wl_util]
        
        bars = ax3.barh(categories, growth_potential, color=['lightgreen', 'lightsalmon'])
        ax3.set_xlim(0, 100)
        ax3.set_xlabel('Growth Headroom (%)')
        ax3.set_title('Expansion Potential')
        
        for bar, growth in zip(bars, growth_potential):
            ax3.text(growth + 2, bar.get_y() + bar.get_height()/2,
                    f'{growth:.1f}%', va='center')
        
        # 4. Decision factors radar chart
        ax4 = fig.add_subplot(gs[2, :], projection='polar')
        
        factors = ['Profit\nMargin', 'Total\nProfit', 'Revenue\nVolume', 
                  'Growth\nPotential', 'Risk\nProfile', 'R&D\nRecovery']
        
        # Normalize scores (0-100)
        cb_scores = [
            cb_margin / (cb_margin + wl_margin) * 100,
            self.analysis['co-branded']['mean_total_profit'] / 
            (self.analysis['co-branded']['mean_total_profit'] + 
             self.analysis['white-label']['mean_total_profit']) * 100,
            30,  # Lower volume score
            (100 - cb_util) / ((100 - cb_util) + (100 - wl_util)) * 100,
            70,  # Lower risk (higher score)
            (self.analysis['co-branded']['mean_total_profit'] / 5.77e6) / 
            ((self.analysis['co-branded']['mean_total_profit'] + 
              self.analysis['white-label']['mean_total_profit']) / 5.77e6) * 100
        ]
        
        wl_scores = [100 - score for score in cb_scores]
        
        angles = np.linspace(0, 2 * np.pi, len(factors), endpoint=False)
        angles = np.concatenate([angles, [angles[0]]])
        
        cb_scores = cb_scores + [cb_scores[0]]
        wl_scores = wl_scores + [wl_scores[0]]
        
        ax4.plot(angles, cb_scores, 'o-', linewidth=2, label='Co-Branded', color='darkgreen')
        ax4.fill(angles, cb_scores, alpha=0.25, color='darkgreen')
        ax4.plot(angles, wl_scores, 's-', linewidth=2, label='White-Label', color='darkorange')
        ax4.fill(angles, wl_scores, alpha=0.25, color='darkorange')
        
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(factors)
        ax4.set_ylim(0, 100)
        ax4.set_title('Strategic Factor Analysis', fontsize=14, fontweight='bold', pad=20)
        ax4.legend(loc='upper right')
        ax4.grid(True)
        
        plt.tight_layout()
        output_path = Path("simulation_results") / f"strategic_insights_{self.timestamp}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved strategic insights to {output_path}")
        plt.close()


def main():
    """Run visualization on latest simulation results"""
    import sys
    
    # Check if a specific file was provided
    if len(sys.argv) > 1:
        analysis_file = sys.argv[1]
        visualizer = SimulationVisualizer(analysis_file)
    else:
        visualizer = SimulationVisualizer()
    
    visualizer.create_all_visualizations()
    print("\n✨ All visualizations created successfully!")


if __name__ == "__main__":
    main() 