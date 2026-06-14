using System;
using System.Security.Cryptography;
using System.Text;

namespace EfnAdapter;

public static class EfnSecurity
{
    private const int ReplayWindowSeconds = 300;

    public static bool VerifySignature(string apiSecret, string timestamp, byte[] rawBody, string signature)
    {
        if (!long.TryParse(timestamp, out var ts)) return false;
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        if (Math.Abs(now - ts) > ReplayWindowSeconds) return false;

        var key = Encoding.UTF8.GetBytes(apiSecret);
        using var mac = new HMACSHA256(key);
        mac.TransformBlock(Encoding.UTF8.GetBytes(timestamp), 0, timestamp.Length, null, 0);
        mac.TransformBlock(Encoding.UTF8.GetBytes("."), 0, 1, null, 0);
        mac.TransformFinalBlock(rawBody, 0, rawBody.Length);
        var expected = "v1=" + Convert.ToBase64String(mac.Hash!);
        return CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(expected), Encoding.UTF8.GetBytes(signature));
    }
}
