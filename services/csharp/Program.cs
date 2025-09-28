using Microsoft.AspNetCore.Mvc;
using System.Drawing;
using System.Drawing.Imaging;

namespace WellnessPlatform.Analytics
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container.
            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            // Add CORS
            builder.Services.AddCors(options =>
            {
                options.AddDefaultPolicy(policy =>
                {
                    policy.AllowAnyOrigin()
                          .AllowAnyMethod()
                          .AllowAnyHeader();
                });
            });

            var app = builder.Build();

            // Configure the HTTP request pipeline.
            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }

            app.UseCors();
            app.UseAuthorization();
            app.MapControllers();

            app.Run();
        }
    }

    [ApiController]
    [Route("api/[controller]")]
    public class AnalyticsController : ControllerBase
    {
        [HttpGet("health")]
        public IActionResult Health()
        {
            return Ok(new
            {
                status = "healthy",
                service = "analytics",
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            });
        }

        [HttpPost("mood-analysis")]
        public IActionResult AnalyzeMood([FromBody] MoodAnalysisRequest request)
        {
            try
            {
                // Simple mood analysis algorithm
                var moodScore = CalculateMoodScore(request.Messages);
                var trends = AnalyzeTrends(request.HistoricalData);
                
                return Ok(new MoodAnalysisResponse
                {
                    MoodScore = moodScore,
                    Trend = trends.Trend,
                    Confidence = trends.Confidence,
                    Recommendations = GenerateRecommendations(moodScore),
                    Timestamp = DateTime.UtcNow
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpGet("progress/{userId}")]
        public IActionResult GetProgress(int userId)
        {
            try
            {
                // Mock progress data for now
                var progress = new ProgressReport
                {
                    UserId = userId,
                    OverallScore = Random.Shared.Next(60, 95),
                    WeeklyImprovement = Random.Shared.Next(-5, 15),
                    SessionCount = Random.Shared.Next(10, 50),
                    LastActivity = DateTime.UtcNow.AddHours(-Random.Shared.Next(1, 48)),
                    MoodTrend = "improving"
                };

                return Ok(progress);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        private double CalculateMoodScore(List<string> messages)
        {
            if (messages == null || messages.Count == 0) 
                return 5.0; // Neutral

            double score = 5.0; // Start neutral
            
            foreach (var message in messages)
            {
                var lowerMessage = message.ToLower();
                
                // Positive indicators
                if (ContainsAny(lowerMessage, new[] { "happy", "good", "better", "great", "wonderful", "excited", "joy" }))
                    score += 1.0;
                    
                // Negative indicators  
                if (ContainsAny(lowerMessage, new[] { "sad", "depressed", "anxious", "worried", "terrible", "awful", "stressed" }))
                    score -= 1.0;
                    
                // Extreme negative (crisis indicators)
                if (ContainsAny(lowerMessage, new[] { "hopeless", "suicide", "worthless", "end it all" }))
                    score -= 2.0;
            }
            
            return Math.Max(1.0, Math.Min(10.0, score)); // Clamp between 1-10
        }

        private (string Trend, double Confidence) AnalyzeTrends(List<double>? historicalData)
        {
            if (historicalData == null || historicalData.Count < 3)
                return ("insufficient_data", 0.0);

            var recentAvg = historicalData.TakeLast(3).Average();
            var olderAvg = historicalData.Take(historicalData.Count - 3).Average();
            
            var diff = recentAvg - olderAvg;
            
            if (Math.Abs(diff) < 0.5)
                return ("stable", 0.7);
            else if (diff > 0)
                return ("improving", Math.Min(0.9, 0.5 + Math.Abs(diff) * 0.1));
            else
                return ("declining", Math.Min(0.9, 0.5 + Math.Abs(diff) * 0.1));
        }

        private List<string> GenerateRecommendations(double moodScore)
        {
            var recommendations = new List<string>();
            
            if (moodScore <= 3.0)
            {
                recommendations.Add("Consider reaching out to a mental health professional");
                recommendations.Add("Practice deep breathing exercises");
                recommendations.Add("Try gentle physical activity like walking");
            }
            else if (moodScore <= 6.0)
            {
                recommendations.Add("Engage in activities you enjoy");
                recommendations.Add("Connect with friends or family");
                recommendations.Add("Practice mindfulness or meditation");
            }
            else
            {
                recommendations.Add("Continue your positive practices");
                recommendations.Add("Consider helping others to maintain wellbeing");
                recommendations.Add("Set new personal goals for growth");
            }
            
            return recommendations;
        }

        private bool ContainsAny(string text, string[] keywords)
        {
            return keywords.Any(keyword => text.Contains(keyword));
        }
    }

    public class MoodAnalysisRequest
    {
        public List<string> Messages { get; set; } = new();
        public List<double>? HistoricalData { get; set; }
    }

    public class MoodAnalysisResponse
    {
        public double MoodScore { get; set; }
        public string Trend { get; set; } = "";
        public double Confidence { get; set; }
        public List<string> Recommendations { get; set; } = new();
        public DateTime Timestamp { get; set; }
    }

    public class ProgressReport
    {
        public int UserId { get; set; }
        public int OverallScore { get; set; }
        public int WeeklyImprovement { get; set; }
        public int SessionCount { get; set; }
        public DateTime LastActivity { get; set; }
        public string MoodTrend { get; set; } = "";
    }
}