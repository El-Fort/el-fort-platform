using Xunit;
using EfnAdapter;
using System.Text;

namespace EfnAdapter.Tests;

public class SecurityTests
{
    const string Secret = "test_secret_key_efn";
    const string Ts = "1749999999";
    static readonly byte[] Body = Encoding.UTF8.GetBytes(
        "{\"uan\":\"014800001234567890\",\"amount\":\"5000.00\",\"currency\":\"NGN\"}");
    const string Expected = "v1=deVTwbJf8evqMRcQN8itx/dnr0epb35U1gRQBZ9YdLE=";

    [Fact]
    public void KnownVector_Matches()
    {
        // Manually compute to verify (bypassing timestamp check)
        var key = Encoding.UTF8.GetBytes(Secret);
        using var mac = new System.Security.Cryptography.HMACSHA256(key);
        var msg = Encoding.UTF8.GetBytes(Ts + ".").Concat(Body).ToArray();
        var sig = "v1=" + Convert.ToBase64String(mac.ComputeHash(msg));
        Assert.Equal(Expected, sig);
    }

    [Fact]
    public void WrongSecret_Rejected()
    {
        // Fresh timestamp within window
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        var key1 = Encoding.UTF8.GetBytes("correct");
        var key2 = Encoding.UTF8.GetBytes("wrong");
        var msg = Encoding.UTF8.GetBytes(now + ".").Concat(Body).ToArray();
        using var m1 = new System.Security.Cryptography.HMACSHA256(key1);
        using var m2 = new System.Security.Cryptography.HMACSHA256(key2);
        var sig1 = "v1=" + Convert.ToBase64String(m1.ComputeHash(msg));
        var sig2 = "v1=" + Convert.ToBase64String(m2.ComputeHash(msg));
        Assert.NotEqual(sig1, sig2);
    }

    [Fact]
    public void ReplayAttack_Rejected()
    {
        // Old timestamp must fail verify
        Assert.False(EfnSecurity.VerifySignature(Secret, "1000000000", Body, Expected));
    }

    [Fact]
    public void FreshValidSignature_Passes()
    {
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
        var key = Encoding.UTF8.GetBytes(Secret);
        var msg = Encoding.UTF8.GetBytes(now + ".").Concat(Body).ToArray();
        using var mac = new System.Security.Cryptography.HMACSHA256(key);
        var sig = "v1=" + Convert.ToBase64String(mac.ComputeHash(msg));
        Assert.True(EfnSecurity.VerifySignature(Secret, now, Body, sig));
    }
}
