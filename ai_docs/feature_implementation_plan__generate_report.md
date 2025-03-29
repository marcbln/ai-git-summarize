# Work Report Generation Feature Implementation Plan

## Configuration File (`projects-groups.yaml`)
```yaml
projects-groups:
  work:
    - /abs/path/to/projectA
    - /abs/path/to/projectB
  private:
    - /abs/path/to/projectC
```

## CLI Command Enhancements
Location: `git_summarize/cli.py`

```python
@cli.command()
@click.option('--group', required=True, help='Project group to analyze')
@click.option('--start-date', required=True, type=click.DateTime())
@click.option('--end-date', required=True, type=click.DateTime())
@click.option('--output-format', default='markdown', 
             type=click.Choice(['markdown', 'json', 'text']))
def generate_report(group, start_date, end_date, output_format):
    """Generate work report for a project group between dates"""
    config = load_project_groups_config()
    if group not in config['projects-groups']:
        raise click.BadParameter(f"Unknown group: {group}")
    
    projects = config['projects-groups'][group]
    report_data = aggregate_project_data(projects, start_date, end_date)
    generate_output(report_data, output_format)
```

## Implementation Phases

### 1. Config Validation
- Verify all paths in group exist
- Check date ranges are valid
- Validate YAML structure

### 2. Git History Aggregation
- Cross-project commit collection
- Date filtering
- Author contribution statistics
- File change metrics

### 3. AI Analysis
- Commit message summarization
- Trend identification
- Code change impact assessment
- Work pattern recognition

### 4. Report Output
#### Markdown Format
```markdown
# Work Report for [Group] ([Start] to [End])

## Project Summary
- Total commits: X
- Contributors: A, B, C
- Files changed: Y

## Key Activities
- Feature development (X commits)
- Bug fixes (Y commits)

## Top Contributors
1. Author A (X commits)
2. Author B (Y commits)
```

#### JSON Format
```json
{
  "period": {
    "start": "2025-03-01",
    "end": "2025-03-29"
  },
  "metrics": {
    "total_commits": 42,
    "files_changed": 128,
    "authors": [...]
  }
}
```

## Risk Analysis
- **Path Validation**: Need to handle invalid/missing project paths
- **Date Handling**: Timezone awareness in date comparisons
- **Performance**: Large project groups may require optimization
- **Output Formats**: Maintaining consistency across formats

## Next Steps
1. Implement configuration loader
2. Create git history aggregation
3. Develop report templates
4. Add CLI integration
