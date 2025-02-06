import pdb
from pythonjsonlogger import jsonlogger
import datetime
import pytz

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        if not log_record.get('source'):
            log_record['source'] = record.name
        if not log_record.get('trace_key'):
            log_record['trace_key'] = record.funcName
        if not log_record.get('caller'):
            log_record['caller'] = f"{record.filename}:{record.lineno}"
        
        for key in ['elasticapm_transaction_id', 'elasticapm_trace_id', 'elasticapm_span_id', 'elasticapm_service_name', 'elasticapm_service_environment', 'elasticapm_labels']:
            if key in log_record:
                del log_record[key]