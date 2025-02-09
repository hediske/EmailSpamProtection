
import dns.resolver

records = dns.resolver.resolve("yahoo.com", 'MX')
mx_record = records[0].exchange
mx_server = str(mx_record).rstrip(".")
print(mx_server)
