app_name = "healthportal"

app {
  env = {}
  port = 8000
  primary_region = "kgl"

  compute {
    cpu      = 1
    memory   = 512
    cpu_kind = "shared"
  }

  process {
    name = "healthportal"
  }
}
