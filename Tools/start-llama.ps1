$env:PYTHONUTF8 = "1"
$p = Start-Process -FilePath "D:\Program files\Llama\llama-server.exe" `
    -ArgumentList '-m "D:\Program files\Llama\Models\Qwen3.5-9B\Qwen3.5-9B-Q4_K_M.gguf" -c 16384 -ngl 99 -fa on -ctk q8_0 -ctv q8_0 -b 1024 -ub 512 -np 1 --no-mmap --host 127.0.0.1 --port 8080 --reasoning off' `
    -NoNewWindow -PassThru
Write-Host "llama-server started (PID: $($p.Id), http://127.0.0.1:8080)"
