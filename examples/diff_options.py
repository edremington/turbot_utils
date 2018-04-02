#!/usr/bin/env python

import turbotutils
import turbotutils.cluster
import turbotutils.guardrails
import argparse
import csv
import sys
import pprint
from inspect import currentframe, getframeinfo


if __name__ == '__main__':
    """ Preforms a guardrail diff of two accounts to allow for easier migration between two accounts and validation"""

    parser = argparse.ArgumentParser(description='diff two turbot account guardrail settings')
    parser.add_argument('source', help='The source account. Use cluster if you wish to use the cluster as a reference')
    parser.add_argument('dest', help='The Destination account')
    args = parser.parse_args()
    if args.source == "cluster":
        filename = 'reports/guardrails/cluster_to_' + args.dest + '.csv'
    else:
        filename = 'reports/guardrails/' +  args.source + '_to_' + args.dest + '.csv'
        
    
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        # Set to False if you do not have a valid certificate for your Turbot Host
        turbot_host_certificate_verification = True

        # Set to your Turbot Host URL
        turbot_host = turbotutils.get_turbot_host()

        # Get the access and secret key pairs
        (turbot_api_access_key, turbot_api_secret_key) = turbotutils.get_turbot_access_keys()
        urn_format = turbotutils.cluster.get_cluster_id(turbot_host, turbot_api_access_key, turbot_api_secret_key, turbot_host_certificate_verification)
        if args.source == 'cluster':
            source_account_urn = urn_format
        else:
            source_account_urn = urn_format + ':' + args.source
        dest_source_account_urn = urn_format + ':' + args.dest
        difference_count = 0

        sourceguardrails = turbotutils.guardrails.get_guardrail_list(turbot_api_access_key, turbot_api_secret_key, turbot_host_certificate_verification,
                                                                     turbot_host,
                                                                     source_account_urn)

        destguardrails = turbotutils.guardrails.get_guardrail_list(turbot_api_access_key, turbot_api_secret_key, turbot_host_certificate_verification,
                                                                   turbot_host,
                                                                   dest_source_account_urn)
        # find any rails in the dest that are not in source (if any)
        # and iterate over that instead of just over source. There WAS a gap if 
        # there were guardrails in dest not in source which in original code would be silently ignored.
        notInFirst = list(set(destguardrails) - set(sourceguardrails))
        railsList = list(set(sourceguardrails)) + notInFirst
        writer.writerow(['Guardrail-Name', 'Source-value', 'Source-requirement','Destination-value','Destination-requirement'])
        print("Finding the guardrail differences between %s and %s" % (args.source, args.dest))
        
        for guardrail in railsList:
            sourceReq=""
            destReq=""
            sourceVal=""
            destVal=""
            sourceBad=False
            destBad=False
            keyVal=""
            try:
                source = sourceguardrails[guardrail]['value']
            except KeyError as e:
                whereErr=args.source
                lineNo = getframeinfo(currentframe()).lineno
                keyVal=str(e.args[0])
                sourceVal='key "'+keyVal+'" missing in '+args.source
                sourceReq='NOT+FOUND'
                sourceBad=True
            try:      
                dest = destguardrails[guardrail]['value']
            except KeyError as e:
                whereErr=args.dest
                lineNo = getframeinfo(currentframe()).lineno
                keyVal=str(e.args[0])
                destVal='key "'+ keyVal +'" missing in '+args.dest
                destReq='NOT+FOUND'
                destBad=True
            if sourceBad == True or destBad == True:
                if sourceVal == "": 
                    if 'value' in source:
                        sourceVal=source['value']
                    elif '$value' in source:
                        sourceVal=source['$value']
                if destVal == "":
                    if 'value' in dest:
                        destVal=dest['value']
                    elif '$value' in dest:
                        dest=dest['$value']
                        
                if sourceReq == "":
                    sourceReq=source['requirement']
                if destReq == "":
                    destReq=dest['requirement']
                print('%s:%s KeyError (guardrail) in "%s" - keyValue: %s' %  ('INFO: ',lineNo,whereErr,keyVal))
                writer.writerow([guardrail, sourceVal, sourceReq, destVal,destReq])
                difference_count += 1
                continue
            if source != dest:
                try:
                    if source['value'] != dest['value']:
                        print('Guardrail "%s" on account "%s" is set to "%s" and on account "%s" is set to "%s"'% (guardrail, args.source, source['value'],args.dest, dest['value']))
                        difference_count += 1
                        sourceVal=source['value']
                        destVal=dest['value']
                except KeyError as e:
                    difference_count += 1
                    if not (str(e.args) in source):
                        whereErr=args.source
                        sourceVal='"'+ str(e.args) +'" not found in "'+args.source+'"'
                    elif not (str(e.args) in dest): 
                        whereErr=args.dest    
                        destVal='"'+ str(e.args) +'" not found in "'+args.dest+'"'
                    else:
                        print("UNKNOWN issue: %s" % e)
                        sys.exit("un-handled exception occurred.")
                    print("%s:%s I got a KeyError in compare. Guardrail: '%s',sourceValue: '%s',destValue: '%s'" %  ('INFO: ',getframeinfo(currentframe()).lineno,guardrail,sourceVal,destVal))
                   
                if sourceVal == "": 
                    sourceVal=source['value']
                if destVal == "":
                    destVal=dest['value']

                writer.writerow([guardrail, sourceVal,source['requirement'], destVal,dest['requirement']])
                    
        if difference_count != 0:
            print('Accounts %s and %s are not in sync, please manually review and rectify this' %(args.source, args.dest))
            print('I found %d differences between these two accounts' % difference_count)
        else:
            print('Accounts %s and %s are in sync' % (args.source, args.dest))
