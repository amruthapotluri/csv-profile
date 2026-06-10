import click
import sys
from csv_profile.profiler import analyze_csv

@click.command()
@click.argument('file_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--missing-threshold', default=0.0, help='Highlight columns with missing data percentages strictly above this value.')
def main(file_path, missing_threshold):
    """Analyze and display profiling insights for a local CSV file."""
    try:
        report = analyze_csv(file_path)
    except Exception as e:
        click.secho(f"Error reading file: {e}", fg="red", err=True)
        sys.exit(1)

    sum_data = report["summary"]
    
    # Render File Summary Header
    click.echo("\n" + "=" * 50)
    click.secho(f" CSV PROFILE REPORT: {sum_data['file_name']}", fg="cyan", bold=True)
    click.echo("=" * 50)
    click.echo(f"Total Rows:    {sum_data['rows']}")
    click.echo(f"Total Columns: {sum_data['columns']}")
    click.echo("-" * 50)

    # Render Column Table Headings
    template = "{:<22} {:<10} {:<12} {:<10} {:<10}"
    click.secho(template.format("Column Name", "Type", "Missing %", "Min Len", "Max Len"), bold=True, underline=True)

    # Render Column Details
    for col in report["columns"]:
        pct = col["missing_percentage"]
        
        # Color warning if missing values exceed threshold
        if pct > missing_threshold:
            row_color = "yellow" if missing_threshold > 0 else "white"
        else:
            row_color = "white"

        click.secho(
            template.format(
                col["column"][:20], 
                col["type"], 
                f"{pct}% ({col['missing_count']})", 
                col["min_length"], 
                col["max_length"]
            ),
            fg=row_color
        )
    click.echo("=" * 50 + "\n")

if __name__ == '__main__':
    main()
