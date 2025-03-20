#!/usr/bin/env python3
# quantum_data_processor.py - Process quantum simulation data and generate visualizations

import argparse
import logging
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import os
import time
from datetime import datetime
import sys

def setup_logging(log_level):
    """Configure logging with specified log level"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)
    return logging.getLogger(__name__)

def ensure_output_dir(output_dir):
    """Ensure the output directory exists"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")
    return output_dir

def get_timestamp():
    """Generate a timestamp string in YYYYMMDD_HHMMSS format"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def parse_arguments():
    """Parse and validate command line arguments"""
    parser = argparse.ArgumentParser(description='Process quantum simulation data and generate visualizations')
    parser.add_argument('--output-dir', type=str, default='output', 
                        help='Directory to save output files (default: output)')
    parser.add_argument('--plot-title', type=str, default='CUDA-Q TensorNet Backend: Scaling to 1100 Qubits',
                        help='Title for the generated plot')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO', help='Set the logging level')
    parser.add_argument('--show-inset', action='store_true', 
                        help='Enable the inset subplot for small qubit counts')
    parser.add_argument('--dpi', type=int, default=300,
                        help='DPI for saved images (default: 300)')
    parser.add_argument('--fig-width', type=float, default=14,
                        help='Figure width in inches (default: 14)')
    parser.add_argument('--fig-height', type=float, default=10,
                        help='Figure height in inches (default: 10)')
    
    return parser.parse_args()

def load_data():
    """Load sample quantum simulation data"""
    logging.info("Loading quantum simulation data")
    
    data = [
        (15, 1.1619),
        (20, 1.5478),
        (25, 13.3674),
        (30, 14.7032),
        (35, 15.4942),
        (40, 22.5259),
        (45, 29.9186),
        (50, 38.2380),
        (55, 39.3430),
        (60, 34.7131),
        (65, 44.5665),
        (70, 45.2972),
        (75, 66.2575),
        (100, 100.2035),
        (105, 97.2727),
        (110, 114.7073),
        (115, 121.1994),
        (120, 119.1005),
        (125, 135.8521),
        (130, 137.0796),
        (135, 154.6344),
        (140, 154.9358),
        (145, 177.2134),
        (150, 172.9061),
        (155, 177.3675),
        (160, 205.8219),
        (165, 202.7780),
        (170, 227.8775),
        (175, 246.0370),
        (180, 245.0758),
        (185, 265.7693),
        (190, 268.5873),
        (195, 305.8181),
        (200, 308.9299),
        (300, 570.8864),
        (350, 828.6885),
        (400, 1111.2337),
        (450, 1380.9539),
        (500, 1675.3307),
        (550, 1942.1153),
        (600, 2154.4481),
        (650, 2524.4808),
        (700, 2923.8830),
        (750, 3515.5221),
        (800, 4145.7131),
        (850, 4673.0538),
        (900, 5220.9250),
        (950, 5893.7584),
        (1000, 6480.2444),
        (1050, 7120.5210),
        (1100, 7619.0218)
    ]
    
    qubits, times = zip(*data)
    return np.array(qubits), np.array(times), data

def create_visualization(qubits, times, data, args):
    """Create visualization of quantum simulation data"""
    logging.info("Creating visualization")
    
    plt.figure(figsize=(args.fig_width, args.fig_height))
    
    # Track progress
    total_steps = 8
    current_step = 0
    
    # Plot main data
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Plotting main data")
    plt.plot(times, qubits, 'bo-', markersize=6, alpha=0.7)
    
    # Add reference line for traditional simulation limit
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Adding reference lines")
    plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, 
               label='Traditional simulation limit (~50 qubits)')
    
    # Mark specific points of interest
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Marking points of interest")
    special_points = [100, 500, 1000, 1100]
    for qubit in special_points:
        for i, (q, t) in enumerate(data):
            if q == qubit:
                plt.plot(t, q, 'ro', markersize=8)
                plt.annotate(f"{q} qubits: {t/60:.1f} min", (t, q), textcoords="offset points", 
                            xytext=(10, 0), fontsize=10)
                break
    
    # Add time reference lines
    time_references = [(3600, "1 hour"), (7200, "2 hours")]
    for t, label in time_references:
        plt.axvline(x=t, color='gray', linestyle=':', alpha=0.7)
        plt.text(t, min(qubits), label, rotation=90, verticalalignment='bottom')
    
    # Add labels and title
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Adding labels and title")
    plt.title(args.plot_title, fontsize=18)
    plt.xlabel('Execution Time (seconds)', fontsize=14)
    plt.ylabel('Number of Qubits', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12, loc='lower right')
    
    # Add annotations
    plt.figtext(0.5, 0.01, 
               "Note: These tests were performed on a standard PC using CUDA-Q TensorNet backend,\n"
               "demonstrating the significant advantage of tensor network methods over traditional state vector methods.\n"
               "Traditional methods are typically limited to ~30 qubits, while TensorNet can simulate systems with over 1000 qubits.", 
               ha="center", fontsize=11)
    
    # Add hardware reference points
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Adding hardware reference points")
    hardware_qubits = [(127, "IBM Eagle (127)"), (433, "IBM Condor (433)"), (53, "Google Sycamore (53)")]
    for qb, name in hardware_qubits:
        plt.axhline(y=qb, color='green', linestyle='-.', alpha=0.5)
        plt.text(min(times), qb, name, verticalalignment='center')
    
    # Calculate polynomial fit
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Calculating polynomial fit")
    z = np.polyfit(times, qubits, 2)
    p = np.poly1d(z)
    
    # Create points for the fitted curve
    x_fit = np.linspace(0, max(times)*1.1, 1000)
    y_fit = p(x_fit)
    
    # Only show reasonable predictions
    valid_indices = (y_fit >= 0) & (y_fit <= max(qubits)*1.1)
    plt.plot(x_fit[valid_indices], y_fit[valid_indices], 'g--', alpha=0.5, label='Fitted curve')
    
    # Add inset with focus on smaller qubit counts (only if explicitly enabled)
    if args.show_inset:
        current_step += 1
        logging.info(f"Progress: {current_step}/{total_steps} - Adding inset")
        ax_inset = plt.axes([0.2, 0.2, 0.35, 0.35])
        ax_inset.plot(times[:20], qubits[:20], 'ro-', markersize=4)
        ax_inset.set_title('Detail: 15-100 Qubits', fontsize=10)
        ax_inset.grid(True, alpha=0.3)
        ax_inset.set_xlabel('Time (seconds)', fontsize=8)
        ax_inset.set_ylabel('Qubits', fontsize=8)
    else:
        current_step += 1
        logging.info(f"Progress: {current_step}/{total_steps} - No inset being added (default)")
    
    # Final layout adjustments
    current_step += 1
    logging.info(f"Progress: {current_step}/{total_steps} - Finalizing layout")
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    
    return plt, p

def calculate_statistics(qubits, times, data, p):
    """Calculate and return various statistics about the data"""
    logging.info("Calculating statistics")
    
    stats = {}
    stats["max_qubits"] = max(qubits)
    
    # Find time to simulate 1000 qubits
    idx_1000 = qubits.tolist().index(1000)
    stats["time_1000_qubits"] = times[idx_1000]/60  # in minutes
    
    # Calculate time ratios
    special_points = [100, 500, 1000, 1100]
    scaling_ratios = []
    
    for i in range(len(special_points)-1):
        q1, q2 = special_points[i], special_points[i+1]
        t1 = times[qubits.tolist().index(q1)]
        t2 = times[qubits.tolist().index(q2)]
        ratio = t2/t1
        qbit_ratio = q2/q1
        scaling_ratios.append((q1, q2, qbit_ratio, ratio))
    
    stats["scaling_ratios"] = scaling_ratios
    
    # Calculate qubit estimates for different times
    time_estimates = []
    for minutes in [1, 5, 10, 30, 60, 120]:
        seconds = minutes * 60
        if seconds <= max(times):
            # Find closest points
            idx = np.abs(times - seconds).argmin()
            closest_time = times[idx]
            closest_qubits = qubits[idx]
            time_estimates.append((minutes, closest_qubits, False))
        else:
            # Extrapolate using polynomial
            est_qubits = p(seconds)
            if est_qubits > 0 and est_qubits < max(qubits) * 1.5:
                time_estimates.append((minutes, int(est_qubits), True))
    
    stats["time_estimates"] = time_estimates
    
    return stats

def save_outputs(plt, stats, args):
    """Save visualization and statistics to output directory"""
    timestamp = get_timestamp()
    output_dir = ensure_output_dir(args.output_dir)
    
    # Save plot
    plot_filename = f"{timestamp}_quantum_scaling.png"
    plot_path = os.path.join(output_dir, plot_filename)
    logging.info(f"Saving plot to {plot_path}")
    plt.savefig(plot_path, dpi=args.dpi, bbox_inches='tight')
    
    # Save statistics to text file
    stats_filename = f"{timestamp}_quantum_stats.txt"
    stats_path = os.path.join(output_dir, stats_filename)
    logging.info(f"Saving statistics to {stats_path}")
    
    with open(stats_path, 'w') as f:
        f.write("QUANTUM SIMULATION STATISTICS\n")
        f.write("============================\n\n")
        
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Key Statistics:\n")
        f.write(f"Maximum qubit count: {stats['max_qubits']} qubits\n")
        f.write(f"Time to simulate 1000 qubits: {stats['time_1000_qubits']:.2f} minutes\n\n")
        
        f.write("Time increase ratios:\n")
        for q1, q2, qbit_ratio, time_ratio in stats["scaling_ratios"]:
            f.write(f"From {q1} to {q2} qubits ({qbit_ratio:.1f}x qubits): Time increased by {time_ratio:.2f}x\n")
        
        f.write("\nQubit scaling estimates:\n")
        for minutes, qubits, extrapolated in stats["time_estimates"]:
            if extrapolated:
                f.write(f"{minutes} minutes: ~{qubits} qubits (extrapolated)\n")
            else:
                f.write(f"{minutes} minutes: ~{qubits} qubits\n")
    
    return plot_path, stats_path

def main():
    """Main function to process data and generate outputs"""
    start_time = time.time()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(getattr(logging, args.log_level))
    logger.info("Starting quantum data processing")
    
    try:
        # Ensure output directory exists
        ensure_output_dir(args.output_dir)
        
        # Load data
        qubits, times, data = load_data()
        
        # Create visualization
        plt_obj, poly_fit = create_visualization(qubits, times, data, args)
        
        # Calculate statistics
        stats = calculate_statistics(qubits, times, data, poly_fit)
        
        # Save outputs
        plot_path, stats_path = save_outputs(plt_obj, stats, args)
        
        # Report success
        elapsed_time = time.time() - start_time
        logger.info(f"Processing completed successfully in {elapsed_time:.2f} seconds")
        logger.info(f"Generated files:")
        logger.info(f"  - Plot: {plot_path}")
        logger.info(f"  - Statistics: {stats_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())