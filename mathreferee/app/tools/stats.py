"""
Statistical analysis tool for auditing assumptions and replicability.
Provides structured outputs for statistical validation and risk assessment.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from scipy import stats
import warnings


# JSON Schema for Gemini function calling
STATS_TOOL_SCHEMA = {
    "audit_statistical_test": {
        "name": "audit_statistical_test",
        "description": "Audit a statistical test for assumption violations and validity",
        "parameters": {
            "type": "object",
            "properties": {
                "test_type": {
                    "type": "string",
                    "description": "Type of test (e.g., 't-test', 'anova', 'chi-square', 'regression')"
                },
                "sample_size": {
                    "type": "integer",
                    "description": "Sample size used in the test"
                },
                "assumptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Assumptions claimed (e.g., 'normality', 'independence', 'equal_variance')"
                },
                "p_value": {
                    "type": "number",
                    "description": "Reported p-value"
                }
            },
            "required": ["test_type", "sample_size"]
        }
    },
    "assess_replicability_risk": {
        "name": "assess_replicability_risk",
        "description": "Assess replicability risks in a statistical analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "sample_size": {
                    "type": "integer",
                    "description": "Sample size"
                },
                "effect_size": {
                    "type": "number",
                    "description": "Reported effect size (Cohen's d or similar)"
                },
                "p_value": {
                    "type": "number",
                    "description": "Reported p-value"
                },
                "multiple_comparisons": {
                    "type": "integer",
                    "description": "Number of statistical tests performed",
                    "default": 1
                }
            },
            "required": ["sample_size", "p_value"]
        }
    },
    "check_power_analysis": {
        "name": "check_power_analysis",
        "description": "Check if a study has adequate statistical power",
        "parameters": {
            "type": "object",
            "properties": {
                "sample_size": {
                    "type": "integer",
                    "description": "Sample size per group"
                },
                "effect_size": {
                    "type": "number",
                    "description": "Expected or observed effect size"
                },
                "alpha": {
                    "type": "number",
                    "description": "Significance level",
                    "default": 0.05
                }
            },
            "required": ["sample_size", "effect_size"]
        }
    },
    "validate_confidence_interval": {
        "name": "validate_confidence_interval",
        "description": "Validate a reported confidence interval",
        "parameters": {
            "type": "object",
            "properties": {
                "mean": {
                    "type": "number",
                    "description": "Sample mean"
                },
                "ci_lower": {
                    "type": "number",
                    "description": "Lower bound of confidence interval"
                },
                "ci_upper": {
                    "type": "number",
                    "description": "Upper bound of confidence interval"
                },
                "sample_size": {
                    "type": "integer",
                    "description": "Sample size"
                },
                "confidence_level": {
                    "type": "number",
                    "description": "Confidence level (e.g., 0.95)",
                    "default": 0.95
                }
            },
            "required": ["mean", "ci_lower", "ci_upper", "sample_size"]
        }
    }
}


class StatisticalTool:
    """
    Tool for statistical analysis auditing and replicability assessment.
    Returns structured outputs for assumption checking and risk flagging.
    """
    
    def __init__(self):
        """Initialize statistical tool."""
        warnings.filterwarnings('ignore')
    
    def get_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get JSON schemas for all tool functions."""
        return STATS_TOOL_SCHEMA
    
    async def audit_statistical_test(
        self,
        test_type: str,
        sample_size: int,
        assumptions: Optional[List[str]] = None,
        p_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Audit a statistical test for assumption violations.
        
        Args:
            test_type: Type of statistical test
            sample_size: Sample size
            assumptions: Claimed assumptions
            p_value: Reported p-value
            
        Returns:
            Structured audit result
        """
        try:
            violations = []
            warnings_list = []
            
            # Check sample size adequacy
            if sample_size < 30:
                warnings_list.append({
                    "type": "small_sample",
                    "severity": "moderate",
                    "message": f"Sample size ({sample_size}) is small; asymptotic assumptions may not hold"
                })
            
            # Check test-specific assumptions
            if test_type.lower() in ['t-test', 'ttest', 't_test']:
                if assumptions and 'normality' in assumptions:
                    if sample_size < 30:
                        violations.append({
                            "assumption": "normality",
                            "severity": "high",
                            "message": "Normality assumption critical for small samples but not verified"
                        })
                
                if assumptions and 'independence' not in assumptions:
                    warnings_list.append({
                        "type": "missing_assumption",
                        "severity": "high",
                        "message": "Independence assumption not explicitly stated"
                    })
            
            elif test_type.lower() in ['anova']:
                required_assumptions = ['normality', 'independence', 'equal_variance']
                if assumptions:
                    missing = [a for a in required_assumptions if a not in assumptions]
                    if missing:
                        violations.append({
                            "assumption": "missing_assumptions",
                            "severity": "high",
                            "message": f"ANOVA requires: {', '.join(missing)}"
                        })
            
            elif test_type.lower() in ['chi-square', 'chi_square']:
                if sample_size < 50:
                    warnings_list.append({
                        "type": "small_sample",
                        "severity": "moderate",
                        "message": "Chi-square may be unreliable with small samples"
                    })
            
            # Check p-value interpretation
            if p_value is not None:
                if 0.04 < p_value < 0.06:
                    warnings_list.append({
                        "type": "borderline_significance",
                        "severity": "moderate",
                        "message": f"P-value ({p_value:.3f}) is borderline; results may be fragile"
                    })
            
            audit_result = "pass" if not violations else "fail"
            risk_level = "high" if violations else ("moderate" if warnings_list else "low")
            
            return {
                "success": True,
                "test_type": test_type,
                "sample_size": sample_size,
                "audit_result": audit_result,
                "risk_level": risk_level,
                "violations": violations,
                "warnings": warnings_list,
                "recommendations": self._generate_recommendations(test_type, violations, warnings_list)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_type": test_type
            }
    
    async def assess_replicability_risk(
        self,
        sample_size: int,
        p_value: float,
        effect_size: Optional[float] = None,
        multiple_comparisons: int = 1
    ) -> Dict[str, Any]:
        """
        Assess replicability risks in statistical analysis.
        
        Args:
            sample_size: Sample size
            p_value: Reported p-value
            effect_size: Effect size if available
            multiple_comparisons: Number of tests performed
            
        Returns:
            Structured replicability assessment
        """
        try:
            risk_factors = []
            
            # Check for p-hacking indicators
            if 0.04 < p_value < 0.05:
                risk_factors.append({
                    "factor": "borderline_p_value",
                    "severity": "high",
                    "description": "P-value suspiciously close to 0.05 threshold"
                })
            
            # Check for multiple comparisons
            if multiple_comparisons > 1:
                adjusted_alpha = 0.05 / multiple_comparisons  # Bonferroni
                if p_value > adjusted_alpha:
                    risk_factors.append({
                        "factor": "multiple_comparisons",
                        "severity": "high",
                        "description": f"With {multiple_comparisons} tests, adjusted α = {adjusted_alpha:.4f}"
                    })
            
            # Check sample size
            if sample_size < 50:
                risk_factors.append({
                    "factor": "small_sample",
                    "severity": "moderate",
                    "description": f"Small sample size ({sample_size}) increases replication risk"
                })
            
            # Check effect size if provided
            if effect_size is not None:
                if effect_size < 0.2:
                    risk_factors.append({
                        "factor": "small_effect",
                        "severity": "moderate",
                        "description": f"Small effect size ({effect_size:.2f}) harder to replicate"
                    })
            
            # Calculate replicability score (0-100, higher is better)
            base_score = 100
            for factor in risk_factors:
                if factor["severity"] == "high":
                    base_score -= 30
                elif factor["severity"] == "moderate":
                    base_score -= 15
            
            replicability_score = max(0, base_score)
            
            if replicability_score >= 70:
                risk_level = "low"
            elif replicability_score >= 40:
                risk_level = "moderate"
            else:
                risk_level = "high"
            
            return {
                "success": True,
                "replicability_score": replicability_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "sample_size": sample_size,
                "p_value": p_value,
                "multiple_comparisons": multiple_comparisons,
                "recommendations": self._generate_replicability_recommendations(risk_factors)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_power_analysis(
        self,
        sample_size: int,
        effect_size: float,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Check if study has adequate statistical power.
        
        Args:
            sample_size: Sample size per group
            effect_size: Effect size (Cohen's d)
            alpha: Significance level
            
        Returns:
            Structured power analysis result
        """
        try:
            # Calculate power for two-sample t-test
            from statsmodels.stats.power import TTestIndPower
            
            analysis = TTestIndPower()
            power = analysis.solve_power(
                effect_size=effect_size,
                nobs1=sample_size,
                alpha=alpha,
                alternative='two-sided'
            )
            
            # Calculate required sample size for 80% power
            required_n = analysis.solve_power(
                effect_size=effect_size,
                alpha=alpha,
                power=0.8,
                alternative='two-sided'
            )
            
            is_adequate = power >= 0.8
            
            return {
                "success": True,
                "statistical_power": float(power),
                "is_adequate": is_adequate,
                "sample_size": sample_size,
                "effect_size": effect_size,
                "required_sample_size_for_80_power": int(np.ceil(required_n)),
                "power_level": "adequate" if power >= 0.8 else "inadequate",
                "interpretation": self._interpret_power(power)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_confidence_interval(
        self,
        mean: float,
        ci_lower: float,
        ci_upper: float,
        sample_size: int,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Validate a reported confidence interval.
        
        Args:
            mean: Sample mean
            ci_lower: Lower CI bound
            ci_upper: Upper CI bound
            sample_size: Sample size
            confidence_level: Confidence level
            
        Returns:
            Structured validation result
        """
        try:
            # Check if mean is within CI
            mean_in_ci = ci_lower <= mean <= ci_upper
            
            # Calculate margin of error
            margin_of_error = (ci_upper - ci_lower) / 2
            
            # Check symmetry
            lower_distance = mean - ci_lower
            upper_distance = ci_upper - mean
            is_symmetric = abs(lower_distance - upper_distance) < 0.01 * margin_of_error
            
            # Estimate standard error
            # For normal distribution: ME = z * SE
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            estimated_se = margin_of_error / z_score
            
            issues = []
            if not mean_in_ci:
                issues.append({
                    "type": "mean_outside_ci",
                    "severity": "critical",
                    "message": "Mean is outside confidence interval"
                })
            
            if not is_symmetric:
                issues.append({
                    "type": "asymmetric_ci",
                    "severity": "moderate",
                    "message": "Confidence interval is not symmetric around mean"
                })
            
            is_valid = len(issues) == 0
            
            return {
                "success": True,
                "is_valid": is_valid,
                "mean": mean,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "margin_of_error": margin_of_error,
                "is_symmetric": is_symmetric,
                "estimated_standard_error": estimated_se,
                "issues": issues,
                "validation_result": "valid" if is_valid else "invalid"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_recommendations(
        self,
        test_type: str,
        violations: List[Dict],
        warnings: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on audit results."""
        recommendations = []
        
        if violations:
            recommendations.append("Address assumption violations before interpreting results")
        
        if any(w["type"] == "small_sample" for w in warnings):
            recommendations.append("Consider non-parametric alternatives for small samples")
            recommendations.append("Report effect sizes and confidence intervals")
        
        if any(w["type"] == "borderline_significance" for w in warnings):
            recommendations.append("Interpret borderline results with caution")
            recommendations.append("Consider replication or larger sample")
        
        return recommendations
    
    def _generate_replicability_recommendations(
        self,
        risk_factors: List[Dict]
    ) -> List[str]:
        """Generate replicability recommendations."""
        recommendations = []
        
        if any(f["factor"] == "multiple_comparisons" for f in risk_factors):
            recommendations.append("Apply multiple comparison correction (e.g., Bonferroni)")
        
        if any(f["factor"] == "small_sample" for f in risk_factors):
            recommendations.append("Increase sample size for more robust results")
        
        if any(f["factor"] == "borderline_p_value" for f in risk_factors):
            recommendations.append("Pre-register analysis plan to avoid p-hacking concerns")
        
        recommendations.append("Report all analyses performed, not just significant ones")
        recommendations.append("Provide data and code for independent verification")
        
        return recommendations
    
    def _interpret_power(self, power: float) -> str:
        """Interpret statistical power level."""
        if power >= 0.9:
            return "Excellent power to detect effects"
        elif power >= 0.8:
            return "Adequate power (conventional threshold)"
        elif power >= 0.6:
            return "Moderate power; may miss real effects"
        else:
            return "Low power; high risk of Type II error"
