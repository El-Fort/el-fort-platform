using System;
using System.Security.Cryptography;
using System.Text;

namespace EfnUtilityAdapter {
    public static class Security {
        public static bool VerifySignature(string secret, string timestamp, string signature, string body, int windowSecs = 300) {
            try {
                long ts = long.Parse(timestamp);
                long now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
                if (Math.Abs(now - ts) > windowSecs) return false;

                using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
                var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(timestamp + "." + body));
                var expected = Convert.ToHexString(hash).ToLower();
                var provided = signature.Replace("v1=", "");
                return CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(expected), Encoding.UTF8.GetBytes(provided));
            } catch { return false; }
        }
    }
}
