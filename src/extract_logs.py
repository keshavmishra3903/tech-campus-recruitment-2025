#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import mmap
import argparse
from typing import Optional, Tuple
import logging
from pathlib import Path

class LogExtractor:
    def __init__(self, filepath: str, chunk_size: int = 1024 * 1024 * 10):  # 10MB chunks
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.file_size = os.path.getsize(filepath)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _binary_search_date_position(self, target_date: str) -> Tuple[int, int]:
        
        with open(self.filepath, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            
            left, right = 0, self.file_size
            
            # Find approximate start position
            while left < right:
                mid = (left + right) // 2
                mm.seek(max(0, mid - 10))  # Back up a bit to ensure we don't split a date
                mm.readline()  # Skip partial line
                line = mm.readline().decode('utf-8', errors='ignore')
                
                if not line:
                    right = mid
                    continue
                    
                try:
                    current_date = line[:10]  # Extract YYYY-MM-DD
                    if current_date < target_date:
                        left = mid + 1
                    else:
                        right = mid
                except Exception:
                    right = mid
            
            start_pos = max(0, left - self.chunk_size)  # Back up one chunk to ensure we don't miss anything
            
            # Find approximate end position
            next_date = f"{target_date[:8]}{int(target_date[-2:]) + 1:02d}"
            left, right = start_pos, self.file_size
            
            while left < right:
                mid = (left + right) // 2
                mm.seek(max(0, mid - 10))
                mm.readline()
                line = mm.readline().decode('utf-8', errors='ignore')
                
                if not line:
                    right = mid
                    continue
                    
                try:
                    current_date = line[:10]
                    if current_date < next_date:
                        left = mid + 1
                    else:
                        right = mid
                except Exception:
                    right = mid
            
            end_pos = min(self.file_size, right + self.chunk_size)  # Add one chunk to ensure we don't miss anything
            
            mm.close()
            return start_pos, end_pos

    def extract_logs(self, target_date: str, output_file: Optional[str] = None) -> None:
        try:
            # Validate date format
            datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD")

        # Create output directory if it doesn't exist
        if output_file is None:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"output_{target_date}.txt"

        self.logger.info(f"Starting log extraction for date: {target_date}")
        start_pos, end_pos = self._binary_search_date_position(target_date)
        
        self.logger.info(f"Searching between positions {start_pos} and {end_pos}")
        matches_found = 0

        with open(self.filepath, 'rb') as f, open(output_file, 'w') as out_f:
            f.seek(start_pos)
            
            while f.tell() < end_pos:
                chunk = f.read(min(self.chunk_size, end_pos - f.tell()))
                if not chunk:
                    break
                
                lines = chunk.decode('utf-8', errors='ignore').splitlines()
                
                # Handle potential partial lines at chunk boundaries
                if start_pos != 0 and len(lines) > 0:
                    lines = lines[1:]  # Skip first partial line
                
                for line in lines:
                    if line.startswith(target_date):
                        out_f.write(line + '\n')
                        matches_found += 1

        self.logger.info(f"Extraction complete. Found {matches_found} log entries for {target_date}")
        self.logger.info(f"Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Extract logs for a specific date from a large log file')
    parser.add_argument('date', help='Date to extract logs for (YYYY-MM-DD format)')
    parser.add_argument('--input', '-i', required=True, help='Input log file path')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--chunk-size', type=int, default=1024*1024*10,
                       help='Chunk size in bytes (default: 10MB)')

    args = parser.parse_args()

    try:
        extractor = LogExtractor(args.input, chunk_size=args.chunk_size)
        extractor.extract_logs(args.date, args.output)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()