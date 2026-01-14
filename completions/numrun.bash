_numrun_completions() {
    local cur opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    opts="save add list search del tag edit export setup-completion"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        local nums=$(numrun list 2>/dev/null | awk 'NR>2 {print $1}')
        COMPREPLY=( $(compgen -W "${opts} ${nums}" -- ${cur}) )
    fi
}
complete -F _numrun_completions numrun
