#!/usr/bin/env Rscript
# Synthetic teaching data only. No patient data, downloads, or package installation.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("Usage: Rscript --vanilla run-demo.R NEW_OUTPUT_DIRECTORY")
if (!requireNamespace("DESeq2", quietly = TRUE)) {
  stop("DESeq2 is required. Ask the course administrator to prepare the R environment.")
}
out <- args[[1]]
if (file.exists(out)) stop("Output path already exists; choose a new directory.")
suppressPackageStartupMessages(library(DESeq2))
if (!dir.create(out, recursive = TRUE)) stop("Cannot create output directory.")

# Every batch contains 3 Control and 3 Case samples: condition is identifiable.
set.seed(20260929)
meta <- data.frame(
  sample_id = sprintf("S%02d", 1:12),
  patient_id = sprintf("SIM%02d", 1:12),
  condition = factor(rep(rep(c("Control", "Case"), each = 3), 2),
                     levels = c("Control", "Case")),
  batch = factor(rep(c("B1", "B2"), each = 6)))
rownames(meta) <- meta$sample_id
design_matrix <- model.matrix(~ batch + condition, meta)
stopifnot(qr(design_matrix)$rank == ncol(design_matrix))

# 3000 artificial genes. These parameters are not estimates from real patients.
n_genes <- 3000L
gene_id <- sprintf("GENE%04d", seq_len(n_genes))
baseline <- 2^runif(n_genes, 3, 10)
true_lfc <- rep(0, n_genes)
true_lfc[1:150] <- 1.5
true_lfc[151:300] <- -1.5
batch_lfc <- rep(0, n_genes)
batch_lfc[301:700] <- 1.2
dispersion <- 0.08 + 2 / baseline
library_scale <- c(0.8, 1.0, 1.2, 0.9, 1.1, 1.3, 1.2, 0.9, 1.0, 1.1, 0.8, 1.2)
counts_matrix <- vapply(seq_len(nrow(meta)), function(j) {
  mu <- baseline * library_scale[j] *
    2^(true_lfc * (meta$condition[j] == "Case") +
       batch_lfc * (meta$batch[j] == "B2"))
  as.integer(rnbinom(n_genes, mu = mu, size = 1 / dispersion))
}, integer(n_genes))
dimnames(counts_matrix) <- list(gene_id, meta$sample_id)
stopifnot(identical(colnames(counts_matrix), rownames(meta)),
          all(is.finite(counts_matrix)), all(counts_matrix >= 0),
          all(counts_matrix == floor(counts_matrix)))

write_table <- function(x, name) {
  write.csv(x, file.path(out, name), row.names = FALSE, na = "NA")
}
write_matrix <- function(x, name) {
  write_table(data.frame(gene_id = rownames(x), x, check.names = FALSE), name)
}
write_table(meta, "metadata.csv")
write_matrix(counts_matrix, "counts.csv")
write_table(data.frame(gene_id, true_lfc, batch_lfc, dispersion), "synthetic-truth.csv")

# Input is untransformed integer counts. TPM/VST values do not go here.
dds <- DESeqDataSetFromMatrix(counts_matrix, meta, design = ~ batch + condition)
# Demonstration filter only; not a universal clinical or RNA-seq QC threshold.
keep <- rowSums(counts(dds) >= 10) >= 3
dds <- dds[keep, ]
dds <- DESeq(dds, quiet = TRUE)
# Positive LFC means Case > Control after accounting for the recorded batch.
res <- results(dds, contrast = c("condition", "Case", "Control"), alpha = 0.05)
result_table <- data.frame(gene_id = rownames(res), as.data.frame(res))
write_table(result_table, "differential-expression.csv")
norm_counts <- counts(dds, normalized = TRUE)
write_matrix(norm_counts, "normalized-counts.csv")
write_table(data.frame(sample_id = colnames(dds), size_factor = sizeFactors(dds)),
            "size-factors.csv")

# Transformation is for exploration. blind=FALSE does NOT remove batch effects.
vsd <- varianceStabilizingTransformation(dds, blind = FALSE)
vst_matrix <- assay(vsd)
write_matrix(vst_matrix, "vst-matrix.csv")
top <- head(order(apply(vst_matrix, 1, var), decreasing = TRUE), 500)
pca <- prcomp(t(vst_matrix[top, ]), center = TRUE, scale. = FALSE)
variance_pct <- 100 * pca$sdev^2 / sum(pca$sdev^2)
write_table(data.frame(meta, PC1 = pca$x[, 1], PC2 = pca$x[, 2]), "pca-coordinates.csv")

plot_file <- function(name, draw) {
  png(file.path(out, name), width = 1400, height = 1000, res = 150)
  on.exit(dev.off())
  par(mar = c(5, 5, 4, 2) + 0.1)
  draw()
}
group_colors <- ifelse(meta$condition == "Case", "#B34A29", "#176B87")
batch_symbols <- ifelse(meta$batch == "B1", 16, 17)
plot_file("01-pca.png", function() {
  plot(pca$x[, 1:2], col = group_colors, pch = batch_symbols, cex = 1.3,
       ylim = range(pca$x[, 2]) + c(-1, 4),
       xlab = sprintf("PC1 (%.1f%%)", variance_pct[1]),
       ylab = sprintf("PC2 (%.1f%%)", variance_pct[2]),
       main = "SYNTHETIC data: PCA of 500 most variable genes")
  legend("top", c("Control", "Case", "B1", "B2"), horiz = TRUE,
         col = c("#176B87", "#B34A29", "black", "black"),
         pch = c(16, 16, 16, 17), bty = "n", cex = 0.8)
})
plot_file("02-ma.png", function() {
  plotMA(res, alpha = 0.05, main = "SYNTHETIC data: unshrunken Case vs Control LFC")
})
plot_file("03-volcano.png", function() {
  valid <- is.finite(res$log2FoldChange) & !is.na(res$padj)
  plot(res$log2FoldChange[valid], -log10(pmax(res$padj[valid], .Machine$double.xmin)),
       pch = 16, cex = 0.5,
       col = ifelse(res$padj[valid] < 0.05, "#B34A2980", "#65778260"),
       xlab = "log2 fold change: Case / Control (unshrunken)",
       ylab = "-log10(BH adjusted p-value)", main = "SYNTHETIC data: volcano plot")
  abline(h = -log10(0.05), lty = 2)
})
plot_file("04-sample-distance.png", function() {
  sample_distance <- dist(t(vst_matrix))
  sample_order <- hclust(sample_distance, method = "complete")$order
  distance_matrix <- as.matrix(sample_distance)[sample_order, sample_order]
  palette <- rev(hcl.colors(60, "Blues 3"))
  layout(matrix(c(1, 2), nrow = 1), widths = c(5, 1))
  par(mar = c(6, 6, 4, 1))
  image(1:12, 1:12, distance_matrix, col = palette, axes = FALSE,
        xlab = "", ylab = "", main = "SYNTHETIC data: VST sample distances", cex.main = 0.9)
  axis(1, at = 1:12, labels = rownames(distance_matrix), las = 2, cex.axis = 0.8)
  axis(2, at = 1:12, labels = rownames(distance_matrix), las = 2, cex.axis = 0.8)
  box()
  par(mar = c(6, 1, 4, 4))
  scale_values <- seq(0, max(distance_matrix), length.out = 60)
  image(1, scale_values, matrix(scale_values, nrow = 1), col = palette,
        axes = FALSE, xlab = "", ylab = "")
  axis(4, las = 2, cex.axis = 0.8)
  mtext("Distance", side = 3, line = 1, cex = 0.8)
})

# Executable checks for numerical examples in the handout.
psi <- function(inclusion, skipping, inc_length = 1, skip_length = 1) {
  if (inclusion == 0 && skipping == 0) return(NA_real_)
  (inclusion / inc_length) / (inclusion / inc_length + skipping / skip_length)
}
stopifnot(isTRUE(all.equal(psi(80, 20), 0.8)),
          isTRUE(all.equal(psi(80, 20, 200, 100), 2 / 3)),
          is.na(psi(0, 0)),
          isTRUE(all.equal(p.adjust(c(.001, .01, .03, .2), "BH"), c(.004, .02, .04, .2))))
write_table(data.frame(inclusion = c(80, 80, 0), skipping = c(20, 20, 0),
                       inc_length = c(1, 200, 1), skip_length = c(1, 100, 1),
                       PSI = c(psi(80, 20), psi(80, 20, 200, 100), psi(0, 0))),
            "psi-examples.csv")
writeLines(capture.output(sessionInfo()), file.path(out, "sessionInfo.txt"))
writeLines(c(
  "SYNTHETIC TEACHING DATA ONLY. Not a clinical benchmark or biological discovery.",
  "Seed: 20260929; 3000 artificial genes; 12 independent simulated samples.",
  "Design: ~ batch + condition; contrast: Case / Control; alpha: 0.05.",
  "Filter: >=10 counts in >=3 samples (teaching choice only).",
  "LFC values are unshrunken; VST and PCA are not batch-corrected.",
  "No FASTQ processing, alignment, transcript quantification, or splicing test was run.",
  "PSI examples are arithmetic only, not rMATS output.",
  sprintf("Genes retained: %d; finite adjusted p-values: %d; padj < 0.05: %d.",
          nrow(dds), sum(!is.na(res$padj)), sum(res$padj < 0.05, na.rm = TRUE)),
  "All input and mathematical checks passed. See sessionInfo.txt for package versions."
), file.path(out, "run-summary.txt"))
message("Finished. Synthetic teaching output: ", normalizePath(out))
