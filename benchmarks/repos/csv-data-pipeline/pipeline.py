# pipeline.py - CSV Data Processing Pipeline
from typing import List, Dict, Any, Optional
import datetime


class DataPipeline:
    @staticmethod
    def process_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process incoming sales/transaction records:
        1. Strip whitespace from string keys and values.
        2. Convert 'amount' to float. If missing/null or invalid, default to 0.0. Negative amounts should raise ValueError.
        3. Parse 'date' from 'YYYY-MM-DD' or 'DD/MM/YYYY' into standard ISO 'YYYY-MM-DD'. If invalid/missing, skip record.
        4. Aggregate:
           - 'total_revenue': sum of all valid amounts (rounded to 2 decimal places)
           - 'record_count': count of processed valid records
           - 'average_amount': total_revenue / record_count (0.0 if count is 0)
        """
        cleaned_records = []
        total_revenue = 0.0

        for r in records:
            # Clean string fields
            clean_r = {}
            for k, v in r.items():
                k_clean = k.strip() if isinstance(k, str) else k
                v_clean = v.strip() if isinstance(v, str) else v
                clean_r[k_clean] = v_clean

            # Validate amount
            raw_amt = clean_r.get("amount")
            try:
                if raw_amt is None or raw_amt == "":
                    amount = 0.0
                else:
                    amount = float(raw_amt)
            except (ValueError, TypeError):
                amount = 0.0

            # BUG: Missing negative check (should raise ValueError)
            
            # Parse date
            raw_date = clean_r.get("date")
            parsed_date = None
            if raw_date:
                for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        dt = datetime.datetime.strptime(raw_date, fmt)
                        parsed_date = dt.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
            
            # BUG: If date is missing/invalid, it should skip the record, but currently still includes it!
            clean_r["amount"] = amount
            clean_r["date"] = parsed_date
            cleaned_records.append(clean_r)
            total_revenue += amount

        count = len(cleaned_records)
        # BUG: Division by zero when count is 0
        avg = total_revenue / count

        return {
            "records": cleaned_records,
            "total_revenue": round(total_revenue, 2),
            "record_count": count,
            "average_amount": round(avg, 2)
        }
