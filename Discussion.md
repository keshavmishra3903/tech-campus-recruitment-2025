Log Extraction System: Design Journey and Implementation

Solutions Considered

Approach 1: Simple Line-by-Line Reading (Initial Attempt)
My first approach was the most straightforward - reading the file line by line and checking each line's date. This would work well for smaller files but presented significant issues with our 1TB log file:


def extract_logs_naive(filepath, target_date):
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith(target_date):
                print(line)


Challenges Faced:
Memory usage grew linearly with file size. Processing time was O(n) - would need to scan entire 1TB file. 
There was no way to skip irrelevant portions of the file and it would take hours to process a single query

Approach 2: Chunked Reading with Buffer
To address the memory concerns, I modified the solution to read the file in chunks:


def extract_logs_chunked(filepath, target_date, chunk_size=1024*1024):
    with open(filepath, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            process_chunk(chunk, target_date)


Improvements:
-- Constant memory usage regardless of file size
-- Better memory management
-- More sustainable for large files

Remaining Issues:
-- Still needed to read entire file
-- No way to skip to relevant sections
-- Processing time remained O(n)

Approach 3: Index-Based Solution (Considered but Not Implemented)
I considered creating an index file that would map dates to file positions:


{
    "2024-12-01": [0, 1000000],
    "2024-12-02": [1000001, 2000000]
    ...
}


**Pros:**
-- O(1) lookup time
-- Very fast for repeated queries

**Cons:**
-- Would need to maintain a separate index file
-- Index itself would be large for 1TB file
-- Initial index creation would be time-consuming
-- Complex to handle log file updates

Final Solution: Binary Search with Memory Mapping

After analyzing the limitations of previous approaches, I realized we could exploit two key properties of the log file:
1. Logs are chronologically ordered
2. Each log entry starts with a date in a consistent format

This led to the binary search approach with memory mapping.

Optimizations:

1. Position Buffering
2. Encoding Handling
3. Error Management

Challenges Encountered and Solutions

1. Partial Line Reading:
   - Challenge: Binary search could land in middle of log entry
   - Solution: Added logic to find complete line boundaries

2. Memory Efficiency:
   - Challenge: Large files could cause memory spikes.
   - Solution: Implemented chunk-based processing with configurable size

3. Edge Cases:
   - Challenge: Logs spanning chunk boundaries.
   - Solution: Added overlap handling in chunk processing.

4. Performance Tuning:
   - Challenge: Finding optimal chunk size
   - Solution: Tested different sizes, settled on 10MB.

## Steps to Run

2. **Usage:**
   python src/extract_logs.py <date> -i <input-file-path>


   Example:
   python src/extract_logs.py 2024-12-01 -i /path/to/logfile.log

3. **Optional Arguments:**
   - `-o, --output`: Specify custom output file path
   - `--chunk-size`: Modify chunk size (default: 10MB)
