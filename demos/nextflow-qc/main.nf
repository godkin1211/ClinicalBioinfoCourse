/*
 * Teaching workflow:
 * samplesheet -> one FASTQC task per sample -> one MULTIQC summary.
 */

process FASTQC {
    tag "${sample_id}"
    label 'fastqc'

    publishDir "${params.outdir}/fastqc", mode: 'copy'

    input:
    tuple val(sample_id), path(reads)

    output:
    path "*_fastqc.html", emit: html
    path "*_fastqc.zip",  emit: zip

    script:
    def read_args = reads.collect { read -> "'${read}'" }.join(' ')
    """
    fastqc \
        --threads ${task.cpus} \
        --outdir . \
        ${read_args}
    """

    stub:
    """
    touch ${sample_id}_R1_fastqc.html
    touch ${sample_id}_R1_fastqc.zip
    """
}

process MULTIQC {
    tag 'all_samples'
    label 'multiqc'

    publishDir "${params.outdir}/multiqc", mode: 'copy'

    input:
    path fastqc_archives

    output:
    path 'multiqc_report.html', emit: report
    path 'multiqc_data',        emit: data

    script:
    def multiqc_command = params.seqera_ai ? 'multiqc-seqera.py' : 'multiqc'
    def ai_args = params.seqera_ai ? '--ai --ai-provider seqera' : ''
    // Read inside the container; never interpolate the token into task scripts.
    def ai_setup = params.seqera_ai ? '''
    set +x
    export SEQERA_ACCESS_TOKEN="$(tr -d '\\r\\n' < /run/secrets/seqera_token)"
    test -n "$SEQERA_ACCESS_TOKEN" || { echo 'Empty Seqera token file' >&2; exit 1; }
    ''' : ''
    """
    ${ai_setup}
    ${multiqc_command} \
        --force \
        --outdir . \
        ${ai_args} \
        ${fastqc_archives.join(' ')}
    """

    stub:
    """
    mkdir -p multiqc_data
    touch multiqc_report.html
    touch multiqc_data/multiqc_general_stats.txt
    """
}

workflow {
    if (params.seqera_ai) {
        if (!workflow.profile.tokenize(',').contains('seqera_ai')) {
            error 'Enable AI with -profile seqera_ai (Docker and token mount required)'
        }
        if (!params.seqera_token_file || !params.seqera_token_file.startsWith('/') || params.seqera_token_file.contains("'") || params.seqera_token_file.contains(',')) {
            error 'Provide --seqera_token_file as an absolute file path without quotes or commas'
        }
        if (!file(params.seqera_token_file).isFile()) {
            error 'Seqera token file does not exist or is not a regular file'
        }
        log.info 'Seqera AI enabled: QC report data will be sent to Seqera. Token is read only inside MULTIQC.'
    }
    samples = channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header: true)
        .map { row ->
            def sample_id = row.sample_id?.trim()
            def fastq_1 = row.fastq_1?.trim()
            def fastq_2 = row.fastq_2?.trim()

            if (!sample_id) {
                error "samplesheet row is missing sample_id: ${row}"
            }
            if (!fastq_1) {
                error "sample ${sample_id} is missing fastq_1"
            }

            def reads = [file(fastq_1, checkIfExists: true)]
            if (fastq_2) {
                reads << file(fastq_2, checkIfExists: true)
            }

            tuple(sample_id, reads)
        }

    FASTQC(samples)

    fastqc_archives = FASTQC.out.zip
        .flatten()
        .collect()

    MULTIQC(fastqc_archives)

    workflow.onComplete = {
        log.info """
        ------------------------------------------------------------
        FASTQ QC teaching pipeline completed
        status : ${workflow.success ? 'SUCCESS' : 'FAILED'}
        outdir : ${params.outdir}
        report : ${params.outdir}/multiqc/multiqc_report.html
        ------------------------------------------------------------
        """.stripIndent()
    }
}
