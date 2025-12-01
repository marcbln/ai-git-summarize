# Retry Mechanism with Linear Backoff Implementation Plan

## Overview
This plan implements a retry mechanism with linear backoff for handling 429 (Too Many Requests) errors in the `git-summary` command. The implementation adds configurable retry parameters and linear backoff timing.

## Problem Statement
Currently, the `git-summary` command fails when encountering 429 errors from API providers. Users need configurable retry behavior with linear backoff instead of exponential backoff.

## Solution Design

### 1. CLI Interface Changes

#### New Command-Line Flags
- `--retries INTEGER`: Number of retry attempts (default: 5)
- `--min-wait INTEGER`: Minimum wait time between retries in seconds (default: 2)
- `--max-wait INTEGER`: Maximum wait time between retries in seconds (default: 10)

#### Usage Examples
```bash
# Default behavior (5 retries, 2-10s linear backoff)
git-summary

# Custom retry configuration
git-summary --retries 3 --min-wait 1 --max-wait 5

# Disable retries
git-summary --retries 0
```

### 2. Linear Backoff Algorithm

#### Formula
For retry attempt `i` (0-based indexing):
```
wait_time = min(min_wait + (i * step_size), max_wait)
```

Where:
- `step_size = (max_wait - min_wait) / (max_retries - 1)` when max_retries > 1
- `step_size = 0` when max_retries <= 1

#### Example Progression
With retries=5, min-wait=2s, max-wait=10s:
- Attempt 1: 2s wait
- Attempt 2: 4s wait
- Attempt 3: 6s wait
- Attempt 4: 8s wait
- Attempt 5: 10s wait

### 3. Code Architecture Changes

#### New Files
- `ai_git/retry_utils.py`: Contains retry utility functions

#### Modified Files
- `ai_git/commands/git_summary.py`: Add CLI flags and pass retry parameters
- `ai_git/ai_summarizer.py`: Update API call methods to use retry mechanism
- `ai_git/ai_client.py`: Potentially update if needed for error handling

#### Retry Configuration Object
```python
@dataclass
class RetryConfig:
    max_retries: int = 5
    min_wait: int = 2  # seconds
    max_wait: int = 10  # seconds
    retryable_status_codes: List[int] = [429, 503, 504]
```

### 4. Error Handling Strategy

#### Retryable Errors
- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Unavailable)
- HTTP 504 (Gateway Timeout)
- Network timeouts and connection errors

#### Non-Retryable Errors
- HTTP 400 (Bad Request)
- HTTP 401 (Unauthorized)
- HTTP 403 (Forbidden)
- HTTP 404 (Not Found)

### 5. Implementation Steps

#### Phase 1: Create Retry Utilities
1. Create `ai_git/retry_utils.py` with linear backoff implementation
2. Implement retry decorator/context manager
3. Add comprehensive error handling and logging

#### Phase 2: Update CLI Commands
1. Add retry flags to `git_summary` command
2. Parse and validate retry parameters
3. Pass retry configuration to AI summarizer

#### Phase 3: Update API Layer
1. Modify `_make_api_call` method in `AISummarizer`
2. Integrate retry mechanism with existing error handling
3. Ensure proper error propagation and user feedback

#### Phase 4: Testing
1. Add unit tests for retry utilities
2. Add integration tests for retry scenarios
3. Test with simulated 429 responses
4. Validate CLI flag parsing and behavior

### 6. Backward Compatibility

#### Default Behavior
- Default retries: 5 (increased from current implicit 3)
- Default min-wait: 2s
- Default max-wait: 10s
- Existing behavior preserved when flags not provided

#### Migration Path
- No breaking changes
- Existing users can continue using the tool without modification
- New flags are optional

### 7. Performance Considerations

#### Maximum Wait Time
- Total maximum wait time: `sum(linear_progression(min_wait, max_wait, retries))`
- For default values: 2+4+6+8+10 = 30 seconds maximum

#### Memory Usage
- Minimal additional memory usage
- No caching of retry state between calls

### 8. Logging and Monitoring

#### Retry Logging
- Log each retry attempt with wait time
- Log final failure after all retries exhausted
- Include retry configuration in debug logs

#### User Feedback
- Show retry progress in console output
- Display final error message clearly
- Provide guidance on rate limiting

### 9. Testing Strategy

#### Unit Tests
- Test linear backoff calculation
- Test retry configuration validation
- Test error classification (retryable vs non-retryable)

#### Integration Tests
- Test CLI flag parsing
- Test end-to-end retry behavior
- Test with mock API responses

#### Edge Cases
- Zero retries configuration
- Single retry configuration
- min_wait == max_wait configuration
- Invalid parameter combinations

### 10. Future Enhancements

#### Potential Additions
- Exponential backoff option
- Jitter for backoff timing
- Per-provider retry configurations
- Retry statistics collection

### 11. Implementation Timeline

#### Day 1
- Create retry utilities
- Add CLI flags
- Update API call methods

#### Day 2
- Add comprehensive tests
- Update documentation
- Performance testing

#### Day 3
- Code review and refinement
- Final testing and deployment

## Success Criteria
- [ ] 429 errors are automatically retried with linear backoff
- [ ] CLI flags work as specified
- [ ] Default behavior provides good user experience
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No breaking changes to existing functionality