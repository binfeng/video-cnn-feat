import os, sys, array, shutil
import numpy as np
import logging

logger = logging.getLogger(__file__)
logging.basicConfig(
    format="[%(asctime)s - %(filename)s:line %(lineno)s] %(message)s",
    datefmt='%d %b %H:%M:%S')
logger.setLevel(logging.INFO)

def process(options, feat_dir):
    newname = ''
    if options.ssr:
        newname = 'ssr'
    newname += 'l%d' % options.p
    resfile = os.path.join(feat_dir.rstrip('/\\') + newname, 'feature.bin')
    
    if os.path.exists(resfile):
        if not options.overwrite:
            logger.info('%s exists. skip', resfile)
            return 0
        else:
            logger.info('%s exists. overwrite', resfile)

    with open(os.path.join(feat_dir, 'shape.txt')) as fr:
        nr_of_images, feat_dim = map(int, fr.readline().strip().split())
        fr.close()
        
    offset = np.float32(1).nbytes * feat_dim
    res = array.array('f')
    
    fr = open(os.path.join(feat_dir,'feature.bin'), 'rb')

    if not os.path.exists(os.path.split(resfile)[0]):
        os.makedirs(os.path.split(resfile)[0])

    fw = open(resfile, 'wb')
    logger.info('writing results to %s', resfile)
    
    for i in xrange(nr_of_images):
        res.fromfile(fr, feat_dim)
        vec = res
        if options.ssr:
            vec = [np.sign(x) * np.sqrt(abs(x)) for x in vec]
        if options.p == 1:
            Z = sum(abs(x) for x in vec) + 1e-9
        else:
            Z = np.sqrt(sum([x**2 for x in vec])) + 1e-9
        if i % 1e4 == 0:
            print ('image_%d, norm_%d=%g' % (i, options.p, Z))
        vec = [x/Z for x in vec]
        del res[:]
        vec = np.array(vec, dtype=np.float32)
        vec.tofile(fw)
    fr.close()
    fw.close()
    logger.info('%d lines parsed', nr_of_images)
    shutil.copyfile(os.path.join(feat_dir,'id.txt'), os.path.join(os.path.split(resfile)[0], 'id.txt'))
    
    shapefile = os.path.join(os.path.split(resfile)[0], 'shape.txt')
    with open(shapefile, 'w') as fw:
        fw.write('%d %d' % (nr_of_images, feat_dim))
        fw.close()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    from optparse import OptionParser
    parser = OptionParser(usage="""usage: %prog [options] feat_dir""")
    parser.add_option("--overwrite", default=0, type="int", help="overwrite existing file (default=0)")
    parser.add_option("--ssr", default=0, type="int", help="do signed square root per dim (default=0)")
    parser.add_option("--p", default=2, type="int", help="L_p normalization (default p=2)")
    
    (options, args) = parser.parse_args(argv)
    if len(args) < 1:
        parser.print_help()
        return 1
    assert(options.p in [1, 2])
    return process(options, args[0])
    

if __name__ == "__main__":
    sys.exit(main())
