using Xunit;
using System;
using System.Security.Cryptography;
using System.Text;
using EfnUtilityAdapter;

public class SecurityTests {
    [Fact]
    public void TestSignature() {
        var secret = "test_secret";
        var ts = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        var body = "{\"customer_ref\":\"123\"}";
        
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(ts + "." + body));
        var sig = "v1=" + Convert.ToHexString(hash).ToLower();
        
        Assert.True(Security.VerifySignature(secret, ts, sig, body));
        Assert.False(Security.VerifySignature(secret, ts, "v1=bad", body));
    }
}
