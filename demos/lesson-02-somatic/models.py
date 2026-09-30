"""Simple mixture and independent-read models, not clinical detection limits."""
import math


def expected_vaf(purity, cancer_fraction, mutant_copies, tumor_cn):
    return purity * cancer_fraction * mutant_copies / (purity * tumor_cn + (1-purity)*2)


def main():
    print("scenario\tpurity\tCCF\tmutant_copies\tCN\texpected_VAF")
    for name, p, f, m, c in [("clonal_diploid", .6, 1, 1, 2),
                            ("low_purity", .1, 1, 1, 2),
                            ("subclonal", .6, .5, 1, 2),
                            ("gain_one_mutant_copy", .2, 1, 1, 6),
                            ("gain_three_mutant_copies", .2, 1, 3, 6)]:
        print(f"{name}\t{p}\t{f}\t{m}\t{c}\t{expected_vaf(p,f,m,c):.6f}")
    print("\ndepth\tP_at_least_3_ALT_at_5pct")
    for n in (30, 100, 400):
        prob = 1-sum(math.comb(n,k)*.05**k*.95**(n-k) for k in range(3))
        print(f"{n}\t{prob:.6f}")
    for p in (.2, .6, 1):
        print(f"CN6 purity={p}: log2ratio={math.log2((p*6+(1-p)*2)/2):.6f}")


if __name__ == "__main__":
    main()
