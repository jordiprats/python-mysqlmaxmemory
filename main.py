import sys
import re

def to_human(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

try:
  # pyodine compatibility
  if sys.argv[0]:
    input_str = sys.stdin.read() + "\n"
except Exception as e:
  output = ""
  exc_type, exc_obj, exc_tb = sys.exc_info()
  fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
  print(exc_type, fname, exc_tb.tb_lineno)
  sys.exit("Error: "+str(e))

s_kbs = re.search(r"\bkey_buffer_size\b[^0-9]+([0-9]+)", input_str)
s_qcs = re.search(r"\bquery_cache_size\b[^0-9]+([0-9]+)", input_str)
s_tts = re.search(r"\btmp_table_size\b[^0-9]+([0-9]+)", input_str)
s_ibps = re.search(r"\binnodb_buffer_pool_size\b[^0-9]+([0-9]+)", input_str)
s_iamps = re.search(r"\binnodb_additional_mem_pool_size\b[^0-9]+([0-9]+)", input_str)
s_ilbs = re.search(r"\binnodb_log_buffer_size\b[^0-9]+([0-9]+)", input_str)

s_mc = re.search(r"\bmax_connections\b[^0-9]+([0-9]+)", input_str)
s_muc = re.search(r"\bmax_user_connections\b[^0-9]+([0-9]+)", input_str)

s_sbs = re.search(r"\bsort_buffer_size\b[^0-9]+([0-9]+)", input_str)
s_rbs = re.search(r"\bread_buffer_size\b[^0-9]+([0-9]+)", input_str)
s_rrbs = re.search(r"\bread_rnd_buffer_size\b[^0-9]+([0-9]+)", input_str)
s_jbs = re.search(r"\bjoin_buffer_size\b[^0-9]+([0-9]+)", input_str)
s_ts = re.search(r"\bthread_stack\b[^0-9]+([0-9]+)", input_str)
s_bcs = re.search(r"\bbinlog_cache_size\b[^0-9]+([0-9]+)", input_str)

unable_to_calculate = False
unable_to_calculate_reasons = []

# serverside

try:
  kbs = int(s_kbs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving key_buffer_size ("+str(e)+")")

try:
  s_have_qc = re.search(r"\bhave_query_cache\b[^A-Z]+([A-Z]+)", input_str)

  if s_have_qc.groups()[0] == 'NO':
    qcs = 0
  else:
    qcs = int(s_qcs.groups()[0])

except Exception as e:
  # Removed in MySQL 8.0.3
  qcs = 0

try:
  tts = int(s_tts.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving tmp_table_size ("+str(e)+")")

try:
  ibps = int(s_ibps.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving innodb_buffer_pool_size ("+str(e)+")")

try:
  iamps = int(s_iamps.groups()[0])
except Exception as e:
  iamps = 0

try:
  ilbs = int(s_ilbs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving innodb_buffer_pool_size ("+str(e)+")")

# per connection

try:
  sbs = int(s_sbs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving sort_buffer_size ("+str(e)+")")

try:
  rbs = int(s_rbs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving read_buffer_size ("+str(e)+")")

try:
  rrbs = int(s_rrbs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving read_rnd_buffer_size ("+str(e)+")")

try:
  jbs = int(s_jbs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving join_buffer_size ("+str(e)+")")

try:
  ts = int(s_ts.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving thread_stack ("+str(e)+")")

try:
  bcs = int(s_bcs.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving binlog_cache_size ("+str(e)+")")

if unable_to_calculate:
  print(', '.join(unable_to_calculate_reasons))

# max connections

try:
  mc = int(s_mc.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving max_connections ("+str(e)+")")

try:
  muc = int(s_muc.groups()[0])
except Exception as e:
  unable_to_calculate = True
  unable_to_calculate_reasons.append("error retrieving max_user_connections ("+str(e)+")")

server_total_memory = kbs + qcs + tts + ibps + iamps + ilbs
per_connection = sbs + rbs + rrbs + jbs + ts + bcs

output = ""

output += "Server max memory usage: "+to_human(server_total_memory) + "\n"
output += "Max mem per connection: "+to_human(per_connection) + "\n"
if muc != 0:
  output += "Max mem per user connections: "+to_human(per_connection*muc) + "\n"
output += "Total connections maximum usage: "+to_human(per_connection*mc) + "\n\n"
output += "Max memory usage: "+to_human(server_total_memory+per_connection*mc)

print(output)
