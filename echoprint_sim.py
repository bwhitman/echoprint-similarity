from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys
import base64, zlib


def inflate_code_string(s):
    """ Takes an uncompressed code string consisting of 0-padded fixed-width
        sorted hex and converts it to the standard code string."""
    n = int(len(s) / 10.0) # 5 hex bytes for hash, 5 hex bytes for time (40 bits)

    def pairs(l, n=2):
        """Non-overlapping [1,2,3,4] -> [(1,2), (3,4)]"""
        # return zip(*[[v for i,v in enumerate(l) if i % n == j] for j in range(n)])
        end = n
        res = []
        while end <= len(l):
            start = end - n
            res.append(tuple(l[start:end]))
            end += n
        return res

    # Parse out n groups of 5 timestamps in hex; then n groups of 8 hash codes in hex.
    end_timestamps = n*5
    times = [int(''.join(t), 16) for t in chunker(s[:end_timestamps], 5)]
    codes = [int(''.join(t), 16) for t in chunker(s[end_timestamps:], 5)]

    assert(len(times) == len(codes)) # these should match up!
    return ' '.join('%d %d' % (c, t) for c,t in zip(codes, times))

def chunker(seq, size):
    return [tuple(seq[pos:pos + size]) for pos in xrange(0, len(seq), size)]


def decode_code_string(compressed_code_string):
    compressed_code_string = compressed_code_string.encode('utf8')
    if compressed_code_string == "":
        return ""
    # do the zlib/base64 stuff
    try:
        # this will decode both URL safe b64 and non-url-safe
        actual_code = zlib.decompress(base64.urlsafe_b64decode(compressed_code_string))
    except (zlib.error, TypeError):
        logger.warn("Could not decode base64 zlib string %s" % (compressed_code_string))
        import traceback; logger.warn(traceback.format_exc())
        return None
    # If it is a deflated code, expand it from hex
    if ' ' not in actual_code:
        actual_code = inflate_code_string(actual_code)
    return actual_code

def overlap(code1, code2):
	d = {}
	count1 = 0
	count2 = 0
	score = 0
	for x in code1.split(" ")[::2]:
		count1 = count1 + 1
		d[x] = d.get("x", 0) + 1
	for x in code2.split(" ")[::2]:
		count2 = count2 + 1
		score = score + d.get(x, 0)
	return (score, count1, count2)


# first do
# export SPOTIPY_CLIENT_ID='your client id'
# export SPOTIPY_CLIENT_SECRET='your client secret'


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=False

results = sp.search(q="running up that hill kate bush", limit=1)
running_tid = results['tracks']['items'][0]["uri"]
results = sp.search(q="cloudbusting kate bush", limit=1)
cloudbusting_tid = results['tracks']['items'][0]["uri"]

features = sp.audio_features([running_tid])
for feature in features:
    analysis = sp._get(feature['analysis_url'])
    running_echoprint = decode_code_string(analysis['track']['echoprintstring'])

features = sp.audio_features([cloudbusting_tid])
for feature in features:
    analysis = sp._get(feature['analysis_url'])
    cloudbusting_echoprint = decode_code_string(analysis['track']['echoprintstring'])


local_running_echoprint = decode_code_string(json.load(open('running.json'))[0]["code"])
local_cloudbusting_echoprint = decode_code_string(json.load(open('cloudbusting.json'))[0]["code"])

(score, count1, count2) = overlap(local_running_echoprint, running_echoprint)
print "local Running %d vs remote Running %d : overlap = %d (%2.4f)" % (count1, count2, score, float(score)/count2)

(score, count1, count2) = overlap(local_cloudbusting_echoprint, cloudbusting_echoprint)
print "local Cloudbusting %d vs remote Cloudbusting %d : overlap = %d (%2.4f)" % (count1, count2, score, float(score)/count2)

(score, count1, count2) = overlap(local_running_echoprint, cloudbusting_echoprint)
print "local Running %d vs remote Cloudbusting %d : overlap = %d (%2.4f)" % (count1, count2, score, float(score)/count2)

(score, count1, count2) = overlap(local_running_echoprint, local_running_echoprint)
print "local Running %d vs local Running %d : overlap = %d (%2.4f)" % (count1, count2, score, float(score)/count2)

(score, count1, count2) = overlap(local_running_echoprint, local_cloudbusting_echoprint)
print "local Running %d vs local Cloudbusting %d : overlap = %d (%2.4f)" % (count1, count2, score, float(score)/count2)

