nextflow.enable.dsl = 2

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
    def read_args = reads.collect { it.toString() }.join(' ')
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
    """
    multiqc \
        --force \
        --outdir . \
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
    samples = Channel
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
