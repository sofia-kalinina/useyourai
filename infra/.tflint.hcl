plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

# Disabled until the existing code is cleaned up, so the check can block new findings from the other rules.
rule "terraform_deprecated_index" { enabled = false }
rule "terraform_required_providers" { enabled = false }
rule "terraform_required_version" { enabled = false }
rule "terraform_typed_variables" { enabled = false }
rule "terraform_unused_declarations" { enabled = false }
