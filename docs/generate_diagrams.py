"""
System Architecture and Data Flow Diagrams for SmartCommit
Generates diagrams for Phase 2 report
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

def create_architecture_diagram():
    """Create system architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'SmartCommit System Architecture', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Define colors
    ui_color = '#E3F2FD'  # Light blue
    api_color = '#FFF3E0'  # Light orange
    service_color = '#F3E5F5'  # Light purple
    data_color = '#E8F5E9'  # Light green
    
    # UI Layer
    ui_box = FancyBboxPatch((0.5, 7.5), 2, 1.2, 
                            boxstyle="round,pad=0.1", 
                            edgecolor='#1976D2', facecolor=ui_color, 
                            linewidth=2)
    ax.add_patch(ui_box)
    ax.text(1.5, 8.3, 'Streamlit UI', fontsize=11, fontweight='bold', ha='center')
    ax.text(1.5, 7.9, 'app.py', fontsize=9, ha='center', style='italic')
    
    # API Layer
    api_box = FancyBboxPatch((3.5, 7.5), 2, 1.2, 
                             boxstyle="round,pad=0.1", 
                             edgecolor='#F57C00', facecolor=api_color, 
                             linewidth=2)
    ax.add_patch(api_box)
    ax.text(4.5, 8.3, 'FastAPI Backend', fontsize=11, fontweight='bold', ha='center')
    ax.text(4.5, 7.9, 'main.py', fontsize=9, ha='center', style='italic')
    
    # Config
    config_box = FancyBboxPatch((7, 7.5), 2, 1.2, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='#388E3C', facecolor=data_color, 
                                linewidth=2)
    ax.add_patch(config_box)
    ax.text(8, 8.3, 'Configuration', fontsize=11, fontweight='bold', ha='center')
    ax.text(8, 7.9, 'config.yaml', fontsize=9, ha='center', style='italic')
    
    # Service Layer - Model Service
    model_box = FancyBboxPatch((0.5, 5), 2.5, 1.5, 
                               boxstyle="round,pad=0.1", 
                               edgecolor='#7B1FA2', facecolor=service_color, 
                               linewidth=2)
    ax.add_patch(model_box)
    ax.text(1.75, 6.1, 'Model Service', fontsize=11, fontweight='bold', ha='center')
    ax.text(1.75, 5.7, 'model_service.py', fontsize=9, ha='center', style='italic')
    ax.text(1.75, 5.35, '• Gemini API', fontsize=8, ha='center')
    ax.text(1.75, 5.1, '• Prompt templates', fontsize=8, ha='center')
    
    # Service Layer - Evaluator
    eval_box = FancyBboxPatch((3.5, 5), 2.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              edgecolor='#7B1FA2', facecolor=service_color, 
                              linewidth=2)
    ax.add_patch(eval_box)
    ax.text(4.75, 6.1, 'Evaluator', fontsize=11, fontweight='bold', ha='center')
    ax.text(4.75, 5.7, 'evaluate_simple.py', fontsize=9, ha='center', style='italic')
    ax.text(4.75, 5.35, '• BLEU/ROUGE', fontsize=8, ha='center')
    ax.text(4.75, 5.1, '• Hallucination', fontsize=8, ha='center')
    
    # Service Layer - Git Interface
    git_box = FancyBboxPatch((6.5, 5), 2.5, 1.5, 
                             boxstyle="round,pad=0.1", 
                             edgecolor='#7B1FA2', facecolor=service_color, 
                             linewidth=2)
    ax.add_patch(git_box)
    ax.text(7.75, 6.1, 'Git Interface', fontsize=11, fontweight='bold', ha='center')
    ax.text(7.75, 5.7, 'git_interface.py', fontsize=9, ha='center', style='italic')
    ax.text(7.75, 5.35, '• GitPython', fontsize=8, ha='center')
    ax.text(7.75, 5.1, '• Diff extraction', fontsize=8, ha='center')
    
    # Data Layer
    data_box = FancyBboxPatch((0.5, 2.5), 2.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              edgecolor='#388E3C', facecolor=data_color, 
                              linewidth=2)
    ax.add_patch(data_box)
    ax.text(1.75, 3.6, 'Dataset', fontsize=11, fontweight='bold', ha='center')
    ax.text(1.75, 3.2, 'commitbench_samples.csv', fontsize=8, ha='center', style='italic')
    ax.text(1.75, 2.9, '170 samples', fontsize=8, ha='center')
    
    # Prompt Layer
    prompt_box = FancyBboxPatch((3.5, 2.5), 2.5, 1.5, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='#388E3C', facecolor=data_color, 
                                linewidth=2)
    ax.add_patch(prompt_box)
    ax.text(4.75, 3.6, 'Prompts', fontsize=11, fontweight='bold', ha='center')
    ax.text(4.75, 3.2, 'commit_generation_improved.txt', fontsize=7, ha='center', style='italic')
    ax.text(4.75, 2.9, 'Few-shot examples', fontsize=8, ha='center')
    
    # Results Layer
    results_box = FancyBboxPatch((6.5, 2.5), 2.5, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 edgecolor='#388E3C', facecolor=data_color, 
                                 linewidth=2)
    ax.add_patch(results_box)
    ax.text(7.75, 3.6, 'Results', fontsize=11, fontweight='bold', ha='center')
    ax.text(7.75, 3.2, 'experiment_*.csv', fontsize=8, ha='center', style='italic')
    ax.text(7.75, 2.9, 'Analysis & plots', fontsize=8, ha='center')
    
    # External - Gemini API
    gemini_box = FancyBboxPatch((0.5, 0.3), 2.5, 1, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='#D32F2F', facecolor='#FFEBEE', 
                                linewidth=2, linestyle='--')
    ax.add_patch(gemini_box)
    ax.text(1.75, 0.9, 'Google Gemini 2.0 Flash', fontsize=10, fontweight='bold', ha='center')
    ax.text(1.75, 0.5, '10 RPM rate limit', fontsize=8, ha='center', style='italic')
    
    # Arrows - UI to API
    arrow1 = FancyArrowPatch((2.5, 8.1), (3.5, 8.1),
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=2, color='#666')
    ax.add_patch(arrow1)
    ax.text(3, 8.4, 'HTTP', fontsize=8, ha='center')
    
    # Arrows - API to Services
    arrow2 = FancyArrowPatch((4.5, 7.5), (1.75, 6.5),
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=1.5, color='#666')
    ax.add_patch(arrow2)
    
    arrow3 = FancyArrowPatch((4.5, 7.5), (4.75, 6.5),
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=1.5, color='#666')
    ax.add_patch(arrow3)
    
    arrow4 = FancyArrowPatch((4.5, 7.5), (7.75, 6.5),
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=1.5, color='#666')
    ax.add_patch(arrow4)
    
    # Arrows - Services to Data
    arrow5 = FancyArrowPatch((1.75, 5), (1.75, 4),
                            arrowstyle='<->', mutation_scale=20, 
                            linewidth=1.5, color='#666', linestyle='--')
    ax.add_patch(arrow5)
    
    arrow6 = FancyArrowPatch((4.75, 5), (4.75, 4),
                            arrowstyle='<->', mutation_scale=20, 
                            linewidth=1.5, color='#666', linestyle='--')
    ax.add_patch(arrow6)
    
    arrow7 = FancyArrowPatch((4.75, 5), (7.75, 4),
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=1.5, color='#666', linestyle='--')
    ax.add_patch(arrow7)
    
    # Config to all services
    arrow8 = FancyArrowPatch((8, 7.5), (8, 6.5),
                            arrowstyle='->', mutation_scale=15, 
                            linewidth=1, color='#388E3C', linestyle=':')
    ax.add_patch(arrow8)
    ax.text(8.5, 7, 'Config', fontsize=7, ha='left', color='#388E3C')
    
    # Model to Gemini
    arrow9 = FancyArrowPatch((1.75, 5), (1.75, 1.3),
                            arrowstyle='<->', mutation_scale=20, 
                            linewidth=2, color='#D32F2F')
    ax.add_patch(arrow9)
    ax.text(2.2, 3, 'API calls', fontsize=8, ha='left', color='#D32F2F')
    
    plt.tight_layout()
    plt.savefig('../docs/figures/system_architecture.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: docs/figures/system_architecture.png")
    plt.close()


def create_dataflow_diagram():
    """Create data flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'SmartCommit Data Flow', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Colors
    input_color = '#E8F5E9'
    process_color = '#FFF3E0'
    output_color = '#E3F2FD'
    
    # Step 1: User Input
    step1 = FancyBboxPatch((3.5, 10), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#388E3C', facecolor=input_color, 
                          linewidth=2)
    ax.add_patch(step1)
    ax.text(5, 10.5, '1. User Input', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 10.15, 'Code diff from Git or manual paste', fontsize=9, ha='center')
    
    # Step 2: FastAPI receives request
    step2 = FancyBboxPatch((3.5, 8.8), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#F57C00', facecolor=process_color, 
                          linewidth=2)
    ax.add_patch(step2)
    ax.text(5, 9.3, '2. FastAPI Endpoint', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 8.95, 'POST /generateCommit', fontsize=9, ha='center')
    
    # Step 3: Load config and prompt
    step3 = FancyBboxPatch((3.5, 7.6), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#F57C00', facecolor=process_color, 
                          linewidth=2)
    ax.add_patch(step3)
    ax.text(5, 8.1, '3. Load Configuration', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 7.75, 'config.yaml + prompt template', fontsize=9, ha='center')
    
    # Step 4: Format prompt
    step4 = FancyBboxPatch((3.5, 6.4), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#F57C00', facecolor=process_color, 
                          linewidth=2)
    ax.add_patch(step4)
    ax.text(5, 6.9, '4. Format Prompt', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 6.55, 'Inject diff into {diff} placeholder', fontsize=9, ha='center')
    
    # Step 5: Call Gemini API
    step5 = FancyBboxPatch((3.5, 5.2), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', 
                          linewidth=2)
    ax.add_patch(step5)
    ax.text(5, 5.7, '5. Gemini API Call', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 5.35, 'genai.GenerativeModel.generate_content()', fontsize=8, ha='center')
    
    # Step 6: Extract response
    step6 = FancyBboxPatch((3.5, 4), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#F57C00', facecolor=process_color, 
                          linewidth=2)
    ax.add_patch(step6)
    ax.text(5, 4.5, '6. Extract Message', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 4.15, 'Parse response.text, clean formatting', fontsize=9, ha='center')
    
    # Step 7: Evaluate (optional)
    step7_left = FancyBboxPatch((0.5, 2.8), 2.5, 0.8, 
                               boxstyle="round,pad=0.05", 
                               edgecolor='#7B1FA2', facecolor='#F3E5F5', 
                               linewidth=2)
    ax.add_patch(step7_left)
    ax.text(1.75, 3.3, '7a. Compute Metrics', fontsize=10, fontweight='bold', ha='center')
    ax.text(1.75, 2.95, 'BLEU, ROUGE, Similarity', fontsize=8, ha='center')
    
    step7_right = FancyBboxPatch((7, 2.8), 2.5, 0.8, 
                                boxstyle="round,pad=0.05", 
                                edgecolor='#7B1FA2', facecolor='#F3E5F5', 
                                linewidth=2)
    ax.add_patch(step7_right)
    ax.text(8.25, 3.3, '7b. Detect Hallucination', fontsize=10, fontweight='bold', ha='center')
    ax.text(8.25, 2.95, 'Check token grounding', fontsize=8, ha='center')
    
    # Step 8: Return response
    step8 = FancyBboxPatch((3.5, 1.6), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#1976D2', facecolor=output_color, 
                          linewidth=2)
    ax.add_patch(step8)
    ax.text(5, 2.1, '8. Return JSON Response', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 1.75, '{message, model, latency, metrics}', fontsize=9, ha='center')
    
    # Step 9: Display to user
    step9 = FancyBboxPatch((3.5, 0.4), 3, 0.8, 
                          boxstyle="round,pad=0.05", 
                          edgecolor='#1976D2', facecolor=output_color, 
                          linewidth=2)
    ax.add_patch(step9)
    ax.text(5, 0.9, '9. Display in UI', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 0.55, 'Streamlit renders commit message', fontsize=9, ha='center')
    
    # Arrows
    arrows = [
        ((5, 10), (5, 9.6)),
        ((5, 8.8), (5, 8.4)),
        ((5, 7.6), (5, 7.2)),
        ((5, 6.4), (5, 6)),
        ((5, 5.2), (5, 4.8)),
        ((5, 4), (5, 3.6)),
        ((5, 2.8), (5, 2.4)),
        ((5, 1.6), (5, 1.2)),
    ]
    
    for start, end in arrows:
        arrow = FancyArrowPatch(start, end,
                               arrowstyle='->', mutation_scale=20, 
                               linewidth=2, color='#666')
        ax.add_patch(arrow)
    
    # Side arrows for evaluation
    arrow_left = FancyArrowPatch((5, 3.4), (3, 3.2),
                                arrowstyle='->', mutation_scale=15, 
                                linewidth=1.5, color='#7B1FA2')
    ax.add_patch(arrow_left)
    
    arrow_right = FancyArrowPatch((5, 3.4), (7, 3.2),
                                 arrowstyle='->', mutation_scale=15, 
                                 linewidth=1.5, color='#7B1FA2')
    ax.add_patch(arrow_right)
    
    # Timing annotations
    ax.text(5.5, 5.5, '~600ms', fontsize=8, ha='left', style='italic', color='#D32F2F')
    ax.text(5.5, 3.1, '~50ms', fontsize=8, ha='left', style='italic', color='#7B1FA2')
    
    # Side note for experiment mode
    note_box = FancyBboxPatch((0.3, 6), 2.5, 1.5, 
                             boxstyle="round,pad=0.1", 
                             edgecolor='#666', facecolor='#FAFAFA', 
                             linewidth=1, linestyle='--')
    ax.add_patch(note_box)
    ax.text(1.55, 7.2, 'Experiment Mode', fontsize=9, fontweight='bold', ha='center')
    ax.text(1.55, 6.85, 'Batch process 170', fontsize=8, ha='center')
    ax.text(1.55, 6.55, 'samples with 7s', fontsize=8, ha='center')
    ax.text(1.55, 6.25, 'delays (rate limit)', fontsize=8, ha='center')
    
    plt.tight_layout()
    plt.savefig('../docs/figures/data_flow.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: docs/figures/data_flow.png")
    plt.close()


def create_metrics_comparison_chart():
    """Create bar chart comparing baseline vs improved metrics"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    metrics = ['ROUGE-L', 'Semantic\nSimilarity', 'Quality\nScore', 'Hallucination\nRate']
    baseline = [46.62, 0.1785 * 100, 0.2158 * 100, 77.6]
    improved = [47.90, 0.2952 * 100, 0.2899 * 100, 42.4]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, baseline, width, label='Baseline', color='#FF9800', alpha=0.8)
    bars2 = ax.bar(x + width/2, improved, width, label='Improved', color='#4CAF50', alpha=0.8)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
    
    ax.set_ylabel('Score (%)', fontsize=11, fontweight='bold')
    ax.set_title('Baseline vs Improved System Performance', fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    # Add improvement annotations
    improvements = ['+2.8%', '+65.4%', '+34.4%', '-35.3%']
    colors = ['#4CAF50', '#4CAF50', '#4CAF50', '#4CAF50']
    for i, (imp, color) in enumerate(zip(improvements, colors)):
        y_pos = max(baseline[i], improved[i]) + 5
        ax.text(i, y_pos, imp, ha='center', fontsize=9, 
               fontweight='bold', color=color)
    
    plt.tight_layout()
    plt.savefig('../docs/figures/metrics_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: docs/figures/metrics_comparison.png")
    plt.close()


def create_hallucination_breakdown():
    """Create pie chart of error categories"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    
    categories = ['Hallucination\nErrors', 'Context\nMisunderstanding']
    sizes = [42.4, 57.6]
    colors = ['#EF5350', '#FFA726']
    explode = (0.05, 0)
    
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=categories, 
                                       colors=colors, autopct='%1.1f%%',
                                       shadow=True, startangle=90,
                                       textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    # Enhance percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(14)
        autotext.set_fontweight('bold')
    
    ax.set_title('Error Distribution in Improved System\n(20251127_005526)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add legend with details
    legend_labels = [
        'Hallucination: 72/170 samples\nUngrounded tokens (e.g., invented names)',
        'Context Misunderstanding: 98/170 samples\nWrong operation descriptions'
    ]
    ax.legend(legend_labels, loc='upper left', fontsize=9, 
             bbox_to_anchor=(0.85, 1))
    
    plt.tight_layout()
    plt.savefig('../docs/figures/error_breakdown.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: docs/figures/error_breakdown.png")
    plt.close()


if __name__ == "__main__":
    print("Generating diagrams for Phase 2 report...\n")
    
    create_architecture_diagram()
    create_dataflow_diagram()
    create_metrics_comparison_chart()
    create_hallucination_breakdown()
    
    print("\n" + "="*80)
    print("✅ All diagrams generated successfully!")
    print("="*80)
    print("\nGenerated files:")
    print("  1. docs/figures/system_architecture.png")
    print("  2. docs/figures/data_flow.png")
    print("  3. docs/figures/metrics_comparison.png")
    print("  4. docs/figures/error_breakdown.png")
    print("\nInsert these into the Phase 2 report at appropriate sections.")
